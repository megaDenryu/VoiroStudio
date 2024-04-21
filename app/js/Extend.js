
class ExtendedWebSocket extends WebSocket {
    /** @param {Record<string,string>} obj*/
    sendJson(obj) {
        this.send(JSON.stringify(obj));
    }
}


