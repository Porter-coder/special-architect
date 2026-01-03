#!/usr/bin/env python3
"""
BMI Calculator Application

A comprehensive BMI (Body Mass Index) calculator that supports both metric and 
imperial units, multiple classification standards, and local history storage.

Features:
- Calculate BMI using standard formula
- Support for metric (kg/cm/m) and imperial (pounds/feet-inches) units
- Multiple classification standards (WHO and Asian)
- Local SQLite database for history tracking
- Interactive command-line interface
"""

import sqlite3
import os
from datetime import datetime


class BMICalculator:
    """Main class for BMI calculations and health classification."""
    
    # WHO Classification Standards (World Health Organization)
    WHO_CLASSIFICATION = [
        (30.0, "Obese", "Class III (Severe)"),
        (25.0, "Overweight", "Pre-obese"),
        (18.5, "Normal", "Normal range"),
        (0, "Underweight", "Severe thinness"),
    ]
    
    # Asian Classification Standards
    ASIAN_CLASSIFICATION = [
        (27.5, "Obese", "High risk"),
        (23.0, "Overweight", "Increased risk"),
        (18.5, "Normal", "Low risk"),
        (0, "Underweight", "Malnutrition risk"),
    ]
    
    def __init__(self, standard="WHO"):
        """Initialize the BMI calculator with specified classification standard.
        
        Args:
            standard: Classification standard to use ("WHO" or "ASIAN")
        """
        self.set_standard(standard)
    
    def set_standard(self, standard):
        """Set the classification standard for BMI interpretation.
        
        Args:
            standard: "WHO" for World Health Organization or "ASIAN" for Asian standards
        """
        if standard.upper() == "ASIAN":
            self.standard = "ASIAN"
            self.classification = self.ASIAN_CLASSIFICATION
        else:
            self.standard = "WHO"
            self.classification = self.WHO_CLASSIFICATION
    
    def calculate_bmi(self, weight_kg, height_m):
        """Calculate BMI value from weight and height.
        
        BMI Formula: BMI = weight(kg) / height(m)^2
        
        Args:
            weight_kg: Weight in kilograms
            height_m: Height in meters
            
        Returns:
            float: Calculated BMI value
            
        Raises:
            ValueError: If weight or height is invalid
        """
        if height_m <= 0:
            raise ValueError("Height must be greater than zero")
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than zero")
        
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)
    
    def classify_bmi(self, bmi):
        """Determine BMI classification based on current standard.
        
        Args:
            bmi: BMI value to classify
            
        Returns:
            dict: Classification result with category and description
        """
        for threshold, category, description in self.classification:
            if bmi >= threshold:
                return {
                    "category": category,
                    "description": description,
                    "standard": self.standard
                }
        return {
            "category": "Unknown",
            "description": "Unable to classify",
            "standard": self.standard
        }
    
    def calculate_optimal_weight(self, height_m, bmi_min=18.5, bmi_max=25.0):
        """Calculate optimal weight range for given height.
        
        Args:
            height_m: Height in meters
            bmi_min: Lower BMI limit (default 18.5)
            bmi_max: Upper BMI limit (default 25.0)
            
        Returns:
            dict: Optimal weight range with min and max in kg
        """
        return {
            "min_weight": round(height_m ** 2 * bmi_min, 1),
            "max_weight": round(height_m ** 2 * bmi_max, 1)
        }


class DatabaseManager:
    """Manages SQLite database operations for BMI history."""
    
    def __init__(self, db_path="bmi_history.db"):
        """Initialize database connection and create tables.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create necessary database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    weight_kg REAL NOT NULL,
                    height_m REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    standard TEXT NOT NULL,
                    unit_system TEXT NOT NULL
                )
            ''')
            conn.commit()
    
    def save_record(self, weight_kg, height_m, bmi, category, standard, unit_system):
        """Save a BMI calculation record to the database.
        
        Args:
            weight_kg: Weight in kilograms
            height_m: Height in meters
            bmi: Calculated BMI value
            category: BMI category
            standard: Classification standard used
            unit_system: Unit system (metric/imperial)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bmi_records (date, weight_kg, height_m, bmi, category, standard, unit_system)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), weight_kg, height_m, bmi, category, standard, unit_system))
            conn.commit()
    
    def get_history(self, limit=10):
        """Retrieve BMI calculation history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            list: List of BMI records as dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, date, weight_kg, height_m, bmi, category, standard, unit_system
                FROM bmi_records ORDER BY id DESC LIMIT ?
            ''', (limit,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "date": row[1],
                    "weight_kg": row[2],
                    "height_m": row[3],
                    "bmi": row[4],
                    "category": row[5],
                    "standard": row[6],
                    "unit_system": row[7]
                })
            return records
    
    def clear_history(self):
        """Clear all BMI records from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bmi_records')
            conn.commit()


class BMIApplication:
    """Main application class handling user interactions."""
    
    def __init__(self):
        """Initialize the BMI calculator application."""
        self.calculator = BMICalculator()
        self.db_manager = DatabaseManager()
        self.unit_system = "metric"
    
    def get_metric_input(self):
        """Get weight and height in metric units from user.
        
        Returns:
            tuple: (weight_kg, height_m)
        """
        print("\n--- Metric Input ---")
        weight_kg = float(input("Enter weight (kg): "))
        
        unit = input("Enter height in (1) cm or (2) m: ").strip()
        if unit == "1":
            height_cm = float(input("Enter height (cm): "))
            height_m = height_cm / 100
        else:
            height_m = float(input("Enter height (m): "))
        
        return weight_kg, height_m
    
    def get_imperial_input(self):
        """Get weight and height in imperial units from user.
        
        Returns:
            tuple: (weight_kg, height_m)
        """
        print("\n--- Imperial Input ---")
        weight_lbs = float(input("Enter weight (pounds): "))
        weight_kg = weight_lbs * 0.453592
        
        unit = input("Enter height in (1) inches or (2) feet/inches: ").strip()
        if unit == "1":
            height_inches = float(input("Enter height (inches): "))
            height_m = height_inches * 0.0254
        else:
            feet = int(input("Enter feet: "))
            inches = int(input("Enter inches: "))
            height_inches = feet * 12 + inches
            height_m = height_inches * 0.0254
        
        return weight_kg, height_m
    
    def calculate_and_save(self):
        """Perform BMI calculation and save to database."""
        if self.unit_system == "metric":
            weight_kg, height_m = self.get_metric_input()
        else:
            weight_kg, height_m = self.get_imperial_input()
        
        try:
            bmi = self.calculator.calculate_bmi(weight_kg, height_m)
            classification = self.calculator.classify_bmi(bmi)
            
            print("\n" + "=" * 40)
            print(f"BMI Result: {bmi}")
            print(f"Category: {classification['category']}")
            print(f"Description: {classification['description']}")
            print(f"Standard Used: {classification['standard']}")
            
            # Calculate optimal weight range
            optimal = self.calculator.calculate_optimal_weight(height_m)
            print(f"Optimal Weight Range: {optimal['min_weight']} - {optimal['max_weight']} kg")
            print("=" * 40)
            
            # Save to database
            self.db_manager.save_record(
                weight_kg, height_m, bmi,
                classification['category'],
                classification['standard'],
                self.unit_system
            )
            print("\nRecord saved to history.")
            
        except ValueError as e:
            print(f"Error: {e}")
    
    def view_history(self):
        """Display BMI calculation history."""
        records = self.db_manager.get_history(limit=10)
        
        if not records:
            print("\nNo history records found.")
            return
        
        print("\n" + "=" * 80)
        print(f"{'ID':<5} {'Date':<25} {'Weight(kg)':<12} {'Height(m)':<10} {'BMI':<8} {'Category':<15}")
        print("-" * 80)
        
        for record in records:
            print(f"{record['id']:<5} {record['date']:<25} {record['weight_kg']:<12.2f} "
                  f"{record['height_m']:<10.2f} {record['bmi']:<8.2f} {record['category']:<15}")
        print("=" * 80)
    
    def clear_history(self):
        """Clear all history records."""
        confirm = input("\nAre you sure you want to clear all history? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.db_manager.clear_history()
            print("History cleared successfully.")
        else:
            print("Operation cancelled.")
    
    def change_settings(self):
        """Change application settings."""
        print("\n--- Settings ---")
        
        # Change classification standard
        print("Select Classification Standard:")
        print("1. WHO (World Health Organization)")
        print("2. Asian")
        standard_choice = input("Enter choice (1-2): ").strip()
        
        if standard_choice == "2":
            self.calculator.set_standard("ASIAN")
            print("Classification standard set to: Asian")
        else:
            self.calculator.set_standard("WHO")
            print("Classification standard set to: WHO")
        
        # Change unit system
        print("\nSelect Unit System:")
        print("1. Metric (kg/cm or kg/m)")
        print("2. Imperial (pounds/feet-inches)")
        unit_choice = input("Enter choice (1-2): ").strip()
        
        if unit_choice == "2":
            self.unit_system = "imperial"
            print("Unit system set to: Imperial")
        else:
            self.unit_system = "metric"
            print("Unit system set to: Metric")
    
    def show_menu(self):
        """Display the main menu and handle user selections."""
        print("\n" + "=" * 50)
        print("       BMI Calculator Application")
        print("=" * 50)
        print("1. Calculate BMI")
        print("2. View History")
        print("3. Clear History")
        print("4. Settings")
        print("5. Exit")
        print("-" * 50)
        
        choice = input("Enter your choice (1-5): ").strip()
        return choice
    
    def run(self):
        """Run the main application loop."""
        print("Welcome to the BMI Calculator Application!")
        
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.calculate_and_save()
            elif choice == "2":
                self.view_history()
            elif choice == "3":
                self.clear_history()
            elif choice == "4":
                self.change_settings()
            elif choice == "5":
                print("\nThank you for using BMI Calculator. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number from 1 to 5.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    app = BMIApplication()
    app.run()