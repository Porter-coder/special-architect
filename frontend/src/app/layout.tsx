import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Architectural Studio',
  description: 'AI-powered code generation with real-time workbench',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>
        {children}
      </body>
    </html>
  )
}
