"use client"

import { RemoteProvider, useRemoteMutable, useRemoteObject, useRemoteValue } from "@/lib/remote"

function Counter() {
  const sdApp = useRemoteObject("stable-diffusion")
  const imageData = useRemoteValue(sdApp?.result)
  const [prompt, setPrompt] = useRemoteMutable(sdApp?.prompt)

  let url = null
  if (imageData) {
    const blob = new Blob([imageData], { type: 'image/jpeg' });
    url = URL.createObjectURL(blob);
  }

  return (
    <div className="flex flex-col space-y-3">
      {url ? <img src={url} /> : null}

      <input type="text" value={prompt} onChange={(t) => setPrompt(t.target.value)}
        className="block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
      />
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