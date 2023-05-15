"use client"

import BigButton from "@/components/BigButton"
import { useRemoteObject, useRemoteValue, RemoteProvider } from "@/lib/remote"

function Calculator() {
    const counter = useRemoteObject("calc")
    const display = useRemoteValue(counter?.display)

    return (
        <div className="flex flex-col space-y-3">
            <div className="text-4xl text-center">{display ?? <samp className="text-gray-300">0</samp>}</div>

            <div className="flex space-x-2">
                <BigButton onClick={() => counter?.digit?.send({digit: 7})}>7</BigButton>
                <BigButton onClick={() => counter?.digit?.send({digit: 8})}>8</BigButton>
                <BigButton onClick={() => counter?.digit?.send({digit: 9})}>9</BigButton>
                <BigButton onClick={() => counter?.op?.send({op: "*"})}>&times;</BigButton>
            </div>
            <div className="flex space-x-2">
                <BigButton onClick={() => counter?.digit?.send({digit: 4})}>4</BigButton>
                <BigButton onClick={() => counter?.digit?.send({digit: 5})}>5</BigButton>
                <BigButton onClick={() => counter?.digit?.send({digit: 6})}>6</BigButton>
                <BigButton onClick={() => counter?.op?.send({op: "-"})}>-</BigButton>
            </div>
            <div className="flex space-x-2">
                <BigButton onClick={() => counter?.digit?.send({digit: 1})}>1</BigButton>
                <BigButton onClick={() => counter?.digit?.send({digit: 2})}>2</BigButton>
                <BigButton onClick={() => counter?.digit?.send({digit: 3})}>3</BigButton>
                <BigButton onClick={() => counter?.op?.send({op: "+"})}>+</BigButton>
            </div>
            <div className="flex space-x-2">
                <BigButton onClick={() => counter?.digit?.send({digit: 0})}>0</BigButton>
                <BigButton onClick={() => counter?.press_dot.send()}>.</BigButton>
                <BigButton onClick={() => counter?.eq.send()}>=</BigButton>
                <BigButton onClick={() => counter?.clear.send()}>C</BigButton>
            </div>
        </div>
    )
}

export default function Home() {
    return (
        <RemoteProvider endpoint="ws://localhost:8080/">
            <Calculator />
        </RemoteProvider>
    )
}