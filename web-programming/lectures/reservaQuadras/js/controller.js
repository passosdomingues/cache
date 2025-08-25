import { Controller } from './mvc.js';
import { model } from './model.js';
import { view } from './view.js';

// O controller basicamente inicializa e deixa o modelo e a view conversarem via EventBus.
// Toda lógica de "fluxo" mora aqui quando não pertence ao modelo.

class ReservaController extends Controller {
  init() {
    // define data inicial no input quando a view ainda não existia
    // (view já setou, mas garantimos consistência)
    const s = model.getState();
    if (!s.data) {
      const today = new Date().toISOString().slice(0,10);
      model.setData(today);
    }
    // nada mais a fazer: eventos já estão conectados na view chamando o model
  }
}

new ReservaController({ model, view });
