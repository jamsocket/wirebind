"use client"

import { useRemoteObject, RemoteProvider, useRemoteValue } from "@/lib/remote"

function Timer() {
  const slider = useRemoteObject("slider")
  const value = useRemoteValue(slider?.value)

  return (
    <div className="flex flex-col space-y-3">
      <div className="text-4xl text-center">{value ?? <span className="text-gray-300">0</span>}</div>
      <div className="flex flex-row space-x-4">
        <input type="range" min="0" max="100" value={value ?? 50} onChange={(e) => slider?.value.set(e.target.value)} />
      </div>
    </div>
  )
}

export default function Home() {
  return (
    <RemoteProvider endpoint="ws://localhost:8080/">
      <Timer />
    </RemoteProvider>
  )
}