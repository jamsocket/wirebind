import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex items-center justify-center h-full">
          {children}
        </div>
      </body>
    </html>
  )
}
