"use client"

import { RemoteProvider, useRemoteMutable, useRemoteObject, useRemoteValue } from "@/lib/remote"

type WeightedPrompt = { prompt: string, weight: number }

function WeightedPromptEntry(props: { value: WeightedPrompt, onChange: (v: WeightedPrompt) => void }) {
  const { value, onChange } = props
  return (
    <div className="flex flex-row space-x-3">
      <input type="text" value={value.prompt} onChange={(t) => onChange({ ...value, prompt: t.target.value })}
        className="block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
      />
      <input type="range" min={0} max={2} step={0.1} value={value.weight} onChange={(t) => onChange({ ...value, weight: Number(t.target.value) })} />
    </div>
  )
}

function StableDiffusionUI() {
  const sdApp = useRemoteObject("stable-diffusion")
  const imageData = useRemoteValue(sdApp?.result)
  const [prompts, setPrompts] = useRemoteMutable(sdApp?.prompts)
  const progress = useRemoteValue(sdApp?.progress)

  let url = null
  if (imageData) {
    const blob = new Blob([imageData], { type: 'image/jpeg' });
    url = URL.createObjectURL(blob);
  }

  return (
    <div className="flex flex-col space-y-3">
      <button onClick={() => sdApp?.shuffle_latents.send()} >shuffle latents</button>

      <div>
        <div style={{width: `${progress * 100}%`}} className="h-2 bg-indigo-600"></div>
      </div>

      {url ? <img src={url} /> : null}

      {
        prompts?.map((p: WeightedPrompt, i: number) => <div><WeightedPromptEntry key={i} value={p} onChange={(v) => {
          const newPrompts = [...prompts]
          newPrompts[i] = v
          setPrompts(newPrompts)
        }} />
        <button onClick={
          () => {
            const newPrompts = [...prompts]
            newPrompts.splice(i, 1)
            setPrompts(newPrompts)
          }
        }>-</button>
        </div>)
      }

      <button
        className="inline-block px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white disabled:bg-gray-300 bg-indigo-600 hover:bg-indigo-700"
        disabled={prompts === undefined}
        onClick={() => {
          const newPrompts = [...prompts]
          newPrompts.push({ prompt: "", weight: 1.0 })
          setPrompts(newPrompts)
        }}>+</button>
    </div>
  )
}

export default function Home() {
  return (
    <RemoteProvider endpoint="ws://localhost:8080/">
      <StableDiffusionUI />
    </RemoteProvider>
  )
}