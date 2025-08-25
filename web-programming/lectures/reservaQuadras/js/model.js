import { EventBus, BaseModel } from './mvc.js';

export const bus = new EventBus();

function todayISO() {
  const d = new Date();
  d.setHours(0,0,0,0);
  return d.toISOString().slice(0,10);
}

function key(date, court) { return `${date}::${court}`; }

function load() {
  try { return JSON.parse(localStorage.getItem('reservas.v1') || '{}'); }
  catch { return {}; }
}
function save(db) {
  localStorage.setItem('reservas.v1', JSON.stringify(db));
}

export class ReservaModel extends BaseModel {
  constructor() {
    super(bus);
    this.courts = [
      { id: 'Q1', nome: 'Quadra 1' },
      { id: 'Q2', nome: 'Quadra 2' },
      { id: 'Q3', nome: 'Quadra 3' }
    ];
    this.db = load(); // { "2025-08-25::Q1": { "08:00": {nome:"..."} } }
    this.intervalo = 60;
    this.data = todayISO();
    this.quadra = this.courts[0].id;
  }

  setData(iso) { this.data = iso; this.emit('state:changed'); }
  setQuadra(id) { this.quadra = id; this.emit('state:changed'); }
  setIntervalo(min) { this.intervalo = min; this.emit('state:changed'); }

  listCourts() { return this.courts.slice(); }
  getState() {
    return {
      data: this.data,
      quadra: this.quadra,
      intervalo: this.intervalo,
      reservas: this.getReservas(this.data, this.quadra)
    };
  }

  timeSlots(intervaloMin) {
    const start = 8 * 60;  // 08:00
    const end = 22 * 60;   // 22:00
    const slots = [];
    for (let m = start; m < end; m += intervaloMin) {
      const hh = String(Math.floor(m/60)).padStart(2,'0');
      const mm = String(m%60).padStart(2,'0');
      slots.push(`${hh}:${mm}`);
    }
    return slots;
  }

  getReservas(data, quadra) {
    const k = key(data, quadra);
    return this.db[k] || {};
  }

  reservar({ data, quadra, hora, nome }) {
    const k = key(data, quadra);
    if (!this.db[k]) this.db[k] = {};
    if (this.db[k][hora]) throw new Error('Horário já reservado.');
    this.db[k][hora] = { nome, createdAt: Date.now() };
    save(this.db);
    this.emit('reservas:changed', { data, quadra });
  }

  cancelar({ data, quadra, hora }) {
    const k = key(data, quadra);
    if (this.db[k]?.[hora]) {
      delete this.db[k][hora];
      if (Object.keys(this.db[k]).length === 0) delete this.db[k];
      save(this.db);
      this.emit('reservas:changed', { data, quadra });
    }
  }

  limparDia({ data, quadra }) {
    const k = key(data, quadra);
    if (this.db[k]) {
      delete this.db[k];
      save(this.db);
      this.emit('reservas:changed', { data, quadra });
    }
  }
}

export const model = new ReservaModel();
