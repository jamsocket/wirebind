export default function BigButton(props: { onClick: () => void, children: React.ReactNode, disabled?: boolean }) {
    return (
        <button
            disabled={props.disabled || false}
            className="w-full text-center rounded bg-white px-6 py-4 text-4xl text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            onClick={props.onClick}>
            {props.children}
        </button>
    )
}