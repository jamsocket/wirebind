import { Sender } from "./sender";

export interface RpcMessage {
    call: string,
    args?: Record<string, any>,
    reply: Sender<Response>,
}

export interface EstablishTwoWayChannel<Incoming, Outgoing> {
    incoming: Sender<Incoming>,
    reply: Sender<Sender<Outgoing>>,
}

export interface RemoteObjectRequest<State extends Record<string, any>> {
    stateListener: Sender<State>,
    reply: Sender<Sender<RpcMessage>>,
    typ: string,
    args?: Record<string, any>,
}
