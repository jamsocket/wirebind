import * as cbor from 'cbor';

import { Multiplexer } from './multiplex';
import { RemoteSender, Sender } from './sender';
import { Message } from './types';
import { Packable } from './packable';
import { Atom } from './binds/atom';

const SENDER_TAG = 40987
const SYNC_TAG = 40988

const PACK_TYPES: Record<string, any> = {
    'atom': Atom,
}

export class SenderEncoder {
    multiplexer: Multiplexer

    constructor(multiplexer: Multiplexer) {
        this.multiplexer = multiplexer
    }

    encode(message: Message<any>) {
        const encoder = new cbor.Encoder()
        encoder.addSemanticType(Sender, (encoder: any, sender: Sender<any>) => {
            const channel = this.multiplexer.registerSender(sender)
            encoder.pushAny(new cbor.Tagged(SENDER_TAG, channel))
            return true
        })
        // TODO: add all packable types.
        encoder.addSemanticType(Atom, (encoder: any, packable: Packable) => {
            encoder.pushAny(new cbor.Tagged(SYNC_TAG, packable.pack()))
            return true
        })
        return encoder._encodeAll([message])
    }

    decode(data: Uint8Array): Message<any> {
        return cbor.decodeFirstSync(data, {
            tags: {
                [SENDER_TAG]: (channel: number) => {
                    const sender = new RemoteSender(this.multiplexer, channel)
                    return sender as any
                },
                [SYNC_TAG]: (packed: any) => {
                    const packType = packed['type']
                    if (packType in PACK_TYPES) {
                        let result = null
                        try {
                            result = PACK_TYPES[packType].fromPacked(packed)
                        } catch (e) {
                            console.warn('Error', e)
                        }
                        
                        return result
                    } else {
                        throw new Error(`Unknown pack type: ${packType}`)
                    }
                }
            }
        })
    }
}
