"use client"

import BigButton from "@/components/BigButton"
import { RemoteProvider, useRemoteObject, useRemoteValue } from "@/lib/remote"

function Timer() {
  const timer = useRemoteObject("timer")
  const value = useRemoteValue(timer?.value)

  return (
    <div className="flex flex-col space-y-3">
      <div className="text-4xl text-center">{value ?? <span className="text-gray-300">0</span>}</div>
      <div className="flex flex-row space-x-4">
        <BigButton onClick={() => timer?.start.send()}>Start</BigButton>
        <BigButton onClick={() => timer?.stop.send()}>Pause</BigButton>
        <BigButton onClick={() => timer?.reset.send()}>Reset</BigButton>
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
