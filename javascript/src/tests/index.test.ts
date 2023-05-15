import { expect } from '@jest/globals';
import { RemoteSender, Sender } from '../sender';
import { multiplexPair, Queue } from './util';

describe('Multiplexer', () => {
  it('should dispatch a local message', () => {
    const q = new Queue()
    const sender = new Sender(q.put)

    sender.send("Hello, world!")
    expect(q.get()).toEqual("Hello, world!")
  });

  it('should host a simple server', () => {
    const [server, client] = multiplexPair()

    const q = new Queue()
    server.setRoot(q.put)
    client.sendRoot("Hello, world!")

    expect(q.get()).toEqual("Hello, world!")
  });

  it('should host a simple RPC server', () => {
    const [server, client] = multiplexPair()

    const rpc = (message: { reply: RemoteSender<string> }) => {
      const reply = message.reply
      reply.send("Hello, world!")
    }

    server.setRoot(rpc)

    const q = new Queue()
    const ch = new Sender(q.put)
    client.sendRoot({ "reply": ch })

    expect(q.get()).toEqual("Hello, world!")
  })
});
