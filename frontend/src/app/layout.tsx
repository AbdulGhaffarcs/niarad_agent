import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NIARAD — Study Agent',
  description: 'An AI study companion that remembers what you struggle with.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
