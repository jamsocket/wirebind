
export abstract class Packable {
    abstract pack(): Record<string, any>

    static fromPacked(packed: Record<string, any>): any {
        throw new Error("Not implemented")
    }

    static packType(): string {
        throw new Error("Not implemented")
    }
}