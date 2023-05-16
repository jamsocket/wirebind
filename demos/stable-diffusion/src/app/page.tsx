"use client"

import { RemoteProvider, useRemoteObject, useRemoteValue } from "@/lib/remote"

function Counter() {
  const sdApp = useRemoteObject("stable-diffusion")
  const imageData = useRemoteValue(sdApp?.result)
  
  let url = null
  if (imageData) {
    const blob = new Blob([imageData], { type: 'image/jpeg' });
    url = URL.createObjectURL(blob);
  }

  return (
    <div className="flex flex-col space-y-3">
      { url ? <img src={url} /> : null }
    </div>
  )
}

export default function Home() {
  return (
    <RemoteProvider endpoint="ws://localhost:8080/">
      <Counter />
    </RemoteProvider>
  )
}