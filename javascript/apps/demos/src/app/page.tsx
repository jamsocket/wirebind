"use client"

import BigButton from "@/components/BigButton"
import { RemoteProvider, useRemoteObject, useRemoteValue } from "@/lib/remote"

function Counter() {
  const counter = useRemoteObject("counter")
  const value = useRemoteValue(counter?.count)
  
  return (
    <div className="flex flex-col space-y-3">
      <div className="text-4xl text-center">{value ?? <span className="text-gray-300">0</span>}</div>

      <div className="flex space-x-2">
        <BigButton onClick={() => counter?.inc.send()}>+</BigButton>
        <BigButton onClick={() => counter?.dec.send()}>-</BigButton>
      </div>
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