import { BaseView, bus } from './mvc.js';
import { model } from './model.js';

export class ReservaView extends BaseView {
  constructor() {
    super(document, bus);
    this.elData = this.qs('#input-data');
    this.elQuadra = this.qs('#select-quadra');
    this.elIntervalo = this.qs('#select-intervalo');
    this.elTitulo = this.qs('#titulo-grade');
    this.elSlots = this.qs('#slots');
    this.elLista = this.qs('#lista-reservas');
    this.elLimpar = this.qs('#btn-limpar');

    this.bindUI();
    this.renderAll();

    bus.on('state:changed', () => this.renderAll());
    bus.on('reservas:changed', () => this.renderAll());
  }

  bindUI() {
    // preencher selects
    this.elQuadra.innerHTML = model.listCourts()
      .map(c => `<option value="${c.id}">${c.nome}</option>`).join('');

    this.elData.value = model.getState().data;
    this.elQuadra.value = model.getState().quadra;
    this.elIntervalo.value = String(model.getState().intervalo);

    this.on(this.elData, 'change', e => model.setData(e.target.value));
    this.on(this.elQuadra, 'change', e => model.setQuadra(e.target.value));
    this.on(this.elIntervalo, 'change', e => model.setIntervalo(Number(e.target.value)));
    this.on(this.elLimpar, 'click', () => {
      const s = model.getState();
      if (confirm('Confirmar limpeza das reservas deste dia/quadra?')) {
        model.limparDia({ data: s.data, quadra: s.quadra });
      }
    });
  }

  renderAll() {
    const s = model.getState();
    const titleCourt = model.listCourts().find(c => c.id === s.quadra)?.nome || s.quadra;
    this.elTitulo.textContent = `${titleCourt} — ${this.formatDateBR(s.data)} (${s.intervalo} min)`;
    this.renderSlots(s);
    this.renderLista(s);
  }

  renderSlots({ data, quadra, intervalo, reservas }) {
    const slots = model.timeSlots(intervalo);
    this.elSlots.innerHTML = slots.map(h => {
      const r = reservas[h];
      const ocupado = Boolean(r);
      const status = ocupado ? `<span class="ocupado">Ocupado</span>` : `<span class="livre">Livre</span>`;
      const quem = r ? this.escapeHTML(r.nome) : '—';
      return `
        <div class="slot" data-hora="${h}">
          <h3>${h}</h3>
          <div class="quem">${quem}</div>
          <div>${status}</div>
          ${ocupado
            ? `<button class="cancelar" data-hora="${h}">Cancelar</button>`
            : `<button class="reservar" data-hora="${h}">Reservar</button>`}
        </div>
      `;
    }).join('');

    this.qsa('.slot button.reservar').forEach(btn => {
      this.on(btn, 'click', () => {
        const hora = btn.dataset.hora;
        const nome = prompt(`Nome para a reserva das ${hora}?`)?.trim();
        if (!nome) return;
        try {
          model.reservar({ data, quadra, hora, nome });
        } catch (e) {
          alert(e.message);
        }
      });
    });

    this.qsa('.slot button.cancelar').forEach(btn => {
      this.on(btn, 'click', () => {
        const hora = btn.dataset.hora;
        if (confirm(`Cancelar a reserva das ${hora}?`)) {
          model.cancelar({ data, quadra, hora });
        }
      });
    });
  }

  renderLista({ data, quadra, reservas }) {
    const items = Object.entries(reservas)
      .sort(([a],[b]) => a.localeCompare(b))
      .map(([hora, r]) => {
        const created = new Date(r.createdAt || Date.now());
        return `
          <li>
            <div>
              <strong>${hora}</strong> — ${this.escapeHTML(r.nome)}
              <div class="meta">criado em ${this.formatDateTimeBR(created)}</div>
            </div>
            <button data-hora="${hora}" class="cancelar">Cancelar</button>
          </li>
        `;
      });

    this.elLista.innerHTML = items.join('') || `<li><em>Nenhuma reserva.</em></li>`;

    this.qsa('#lista-reservas .cancelar').forEach(btn => {
      this.on(btn, 'click', () => {
        const hora = btn.dataset.hora;
        if (confirm(`Cancelar a reserva das ${hora}?`)) {
          model.cancelar({ data, quadra, hora });
        }
      });
    });
  }

  formatDateBR(iso) {
    const [y,m,d] = iso.split('-').map(Number);
    const dt = new Date(y, m-1, d);
    return dt.toLocaleDateString('pt-BR', { weekday:'short', day:'2-digit', month:'short', year:'numeric' });
  }
  formatDateTimeBR(dt) {
    return dt.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  }
  escapeHTML(s) { return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }
}

export const view = new ReservaView();
