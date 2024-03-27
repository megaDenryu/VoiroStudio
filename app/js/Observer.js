///@ts-check

class Observer {
    /**@type {{value: any, callback: any}[]}*/ observers;

    constructor() {
        this.observers = [];
    }
    /**
     * 
     * @param {any} value 
     * @param {function} callback 
     */
    watchValue(value, callback) {
        Object.defineProperty(o, p, attributes)

        let obj = { value: value, callback: callback };
        this.observers.push(obj);
    }
}