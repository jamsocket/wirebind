import { Atom, AtomReplica } from '../binds/atom';
import { multiplexPair, Queue } from './util';

describe('Atom', () => {
    it('becomes a replica', () => {
        const atom = new Atom(4)
        const [server, client] = multiplexPair()

        const q = new Queue()
        server.setRoot(q.put)

        client.sendRoot(atom)
        
        expect(q.get()).toBeInstanceOf(AtomReplica)
    });

    it('mirrors updates from the replica', () => {
        const atom = new Atom(4)
        const [server, client] = multiplexPair()

        const q = new Queue()
        server.setRoot(q.put)

        client.sendRoot(atom)

        const replica: AtomReplica = q.get()
        replica.set(5)

        expect(atom.value).toBe(5)
    });

    it('mirrors updates from the server', () => {
        const atom = new Atom(4)
        const [server, client] = multiplexPair()

        const q = new Queue()
        server.setRoot(q.put)

        client.sendRoot(atom)

        const replica: AtomReplica = q.get()
        atom.set(5)

        expect(replica.get()).toBe(5)
    });
});
