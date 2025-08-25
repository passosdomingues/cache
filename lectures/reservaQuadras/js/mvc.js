// micro-framework mvc: EventBus + BaseModel + BaseView + Controller glue

export class EventBus {
  constructor() { this.map = new Map(); }
  on(event, fn) {
    if (!this.map.has(event)) this.map.set(event, new Set());
    this.map.get(event).add(fn);
    return () => this.off(event, fn);
  }
  off(event, fn) { this.map.get(event)?.delete(fn); }
  emit(event, payload) {
    this.map.get(event)?.forEach(fn => fn(payload));
  }
}

export class BaseModel {
  constructor(bus) { this.bus = bus; }
  emit(event, payload) { this.bus.emit(event, payload); }
}

export class BaseView {
  constructor(root, bus) {
    this.root = root;
    this.bus = bus;
  }
  qs(sel) { return this.root.querySelector(sel); }
  qsa(sel) { return Array.from(this.root.querySelectorAll(sel)); }
  on(el, ev, fn) { el.addEventListener(ev, fn); }
  html(el, str) { el.innerHTML = str; }
}

export class Controller {
  constructor({ bus, model, view }) {
    this.bus = bus;
    this.model = model;
    this.view = view;
    if (this.init) this.init();
  }
}
