import javafx.animation.AnimationTimer;
import javafx.application.Application;
import javafx.geometry.VPos;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.image.Image;
import javafx.scene.input.KeyCode;
import javafx.scene.layout.StackPane;
import javafx.scene.paint.*;
import javafx.scene.text.*;
import javafx.stage.Stage;

import java.io.File;
import java.io.InputStream;
import java.util.*;

/**
 * ╔══════════════════════════════════════════════════════════════╗
 * ║       AS ÁGUAS DE APSU: A Lenda dos Apkallu                 ║
 * ║       Jogo 2D side-scroller — JavaFX 21 Canvas              ║
 * ╠══════════════════════════════════════════════════════════════╣
 * ║  ARQUITETURA: Monolito intencional (ver ADR-001)            ║
 * ║  SISTEMA DE COORDS: Mundo vs Tela (ver ADR-003)             ║
 * ║  TIMING: AnimationTimer nanosegundos (ver ADR-004)          ║
 * ╚══════════════════════════════════════════════════════════════╝
 *
 * SEÇÕES DO ARQUIVO:
 *   1. Constantes e Enums
 *   2. Estado do Jogo (campos)
 *   3. Inicialização (start, reset)
 *   4. Input
 *   5. Update (lógica por fase)
 *   6. Render (desenho por fase)
 *   7. Helpers (colisão, partículas, assets)
 */
public class ApsuGame extends Application {

    // =========================================================
    // 1. CONSTANTES E ENUMS
    // =========================================================

    /** Resolução da janela/canvas */
    static final int W = 1366, H = 768;

    /** Bounding boxes das entidades (ver ADR-002 sobre hitbox menor) */
    static final double HERO_W = 56, HERO_H = 80;
    static final double BOSS_W = 110, BOSS_H = 130;
    static final double TAB_W = 34, TAB_H = 46;      // Tabuleta da sabedoria
    static final double ENEMY_W = 42, ENEMY_H = 30;

    /** Tamanho do "mundo" em pixels para Fases 1 e 2 */
    static final double PHASE_LEN = 3600;

    /** HP máximo do boss Kullullû */
    static final int BOSS_MAX_HP = 5;

    /** Estados da máquina de estados principal (ver diagrama em ARCHITECTURE.md) */
    enum State { MENU, DIALOGUE, PHASE1, PHASE2, PHASE3, VICTORY, GAMEOVER }

    /** Modos de dificuldade */
    enum Diff { SABIO, IRA }

    // =========================================================
    // 2. ESTADO DO JOGO
    // =========================================================

    State state = State.MENU;
    Diff  diff  = Diff.SABIO;

    // --- Sprites (null = usar fallback geométrico) ---
    Image imgHero, imgBoss, imgNpc, imgBg1, imgBg2, imgBg3;

    // --- Input ---
    /** Teclas atualmente pressionadas (para movimento contínuo) */
    final Set<KeyCode> keys = new HashSet<>();

    // --- Herói ---
    /**
     * Nas fases com scroll, heroX e' uma coordenada de MUNDO.  Somente na
     * arena fixa (fase 3) ela coincide com a coordenada de tela.  Manter esta
     * regra evita a realimentacao camera/heroi que antes impedia o fim da fase.
     */
    double heroX, heroY;
    boolean facingRight = true;
    int    heroHP;
    boolean invincible;
    long    invStart;       // nanosegundo em que o iframe começou

    // --- Câmera / Mundo ---
    /** Offset horizontal da câmera — tela = mundo - camX */
    double camX;

    // --- Colecionáveis ---
    int    tabs;            // tabuletas coletadas (0 → 3)
    boolean tab1alive = true, tab2alive = true;
    double  tab1X, tab1Y, tab2X, tab2Y;  // coords de MUNDO

    // --- Inimigos: {worldX, screenY, speed, amplitude, baseY, type}
    //   worldX  = posição horizontal no mundo
    //   screenY = posição vertical na tela (calculada via seno)
    //   speed   = velocidade do movimento senoidal
    //   amplitude = amplitude da oscilação vertical
    //   baseY   = centro vertical da oscilação
    //   type    = 0 (peixe), 1 (peixe grande), 2 (caranguejo)
    final List<double[]> enemies = new ArrayList<>();

    // --- Boss ---
    double bossX, bossY;
    int    bossHP;
    long   lastBubbleTime;
    /** Bolhas do boss: {screenX, screenY, vx, vy} */
    final List<double[]> bubbles = new ArrayList<>();

    // --- Projéteis do herói: {screenX, screenY, vx, vy} ---
    final List<double[]> beams = new ArrayList<>();
    long lastShotTime;

    // --- Obstáculos Fase 2 (corais): {worldX, y, width, height} ---
    final List<double[]> corals = new ArrayList<>();

    // --- Easter Egg (Fase 2) ---
    double  chestWorldX, chestY;
    boolean easterFound;
    long    easterShowTime;

    // --- Sistema de Partículas: {x, y, vx, vy, life, r, g, b} ---
    final List<double[]> particles = new ArrayList<>();

    // --- Diálogo ---
    int dlgLine = 0;
    final String[] DLG = {
        "Adapa, meu bravo Apkallu! Sou Enki, senhor das águas primordiais.",
        "O oceano sagrado Apsu foi corrompido por Kullullû,",
        "um Apkallu que se rendeu às sombras do abismo eterno.",
        "Nada pelas Águas Claras e pelas Cavernas de Coral...",
        "Recupera as 3 Tabuletas da Sabedoria perdidas nas profundezas!",
        "Derrota Kullullû no Templo Submerso e purifica o Apsu!",
        "A sabedoria dos ancestrais guia tua nadadeira.  [ ESPAÇO → Iniciar ]"
    };

    // --- Menu ---
    /** 0=Sábio, 1=Ira, 2=Iniciar, 3=Créditos */
    int     menuSel     = 2;
    boolean showCredits = false;

    // --- Notificações temporárias (alertas de fase, tabuletas) ---
    String alertMsg  = "";
    long   alertTime = 0;

    // --- Timestamp atual em nanosegundos (atualizado pelo AnimationTimer) ---
    long nano;

    // =========================================================
    // 3. INICIALIZAÇÃO
    // =========================================================

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) {
        Canvas     canvas = new Canvas(W, H);
        GraphicsContext gc = canvas.getGraphicsContext2D();
        Scene scene = new Scene(new StackPane(canvas), W, H, Color.BLACK);

        // Carregar assets — null se não encontrado (fallback geométrico)
        imgHero = loadImg("hero.png");
        imgBoss = loadImg("boss.png");
        imgNpc  = loadImg("npc.png");
        imgBg1  = loadImg("bg1.png");
        imgBg2  = loadImg("bg2.png");
        imgBg3  = loadImg("bg3.png");

        // Input: teclado contínuo (Set) + eventos pontuais (onKey)
        scene.setOnKeyPressed(e  -> { keys.add(e.getCode()); onKey(e.getCode()); });
        scene.setOnKeyReleased(e -> keys.remove(e.getCode()));

        // Game loop principal — ~60 FPS via VSync
        new AnimationTimer() {
            @Override
            public void handle(long now) {
                nano = now;
                update();
                render(gc);
            }
        }.start();

        stage.setTitle("As Águas de Apsu: A Lenda dos Apkallu");
        stage.setScene(scene);
        stage.setFullScreen(true);
        stage.setFullScreenExitHint("");  // remove hint "pressione ESC"
        stage.show();
    }

    /** Reinicia todos os campos para começar uma nova partida */
    void reset() {
        heroHP    = (diff == Diff.SABIO) ? 5 : 3;
        tabs      = 0;
        camX      = 0;
        heroX     = 80;
        heroY     = H / 2.0 - HERO_H / 2;
        facingRight = true;
        invincible  = false;
        tab1alive   = true;
        tab2alive   = true;
        easterFound = false;
        easterShowTime = 0;
        beams.clear();
        bubbles.clear();
        enemies.clear();
        corals.clear();
        particles.clear();
        alertMsg = "";
        lastShotTime = 0;
        lastBubbleTime = nano;
    }

    // --- Início das Fases ---

    void startPhase1() {
        double spd = (diff == Diff.SABIO) ? 1.15 : 2.1;
        enemies.clear();
        // Inimigos distribuídos ao longo do mundo (worldX)
        enemies.add(new double[]{ 850,  H * .45, spd, 75, H * .45, 0 });
        enemies.add(new double[]{ 1750, H * .32, spd, 65, H * .32, 1 });
        enemies.add(new double[]{ 2650, H * .56, spd, 80, H * .56, 0 });
        // Tabuleta 1 perto do fim do mundo
        tab1X = PHASE_LEN - 280;
        tab1Y = H / 2.0 - TAB_H / 2;
        state = State.PHASE1;
        showAlert("⚓ Fase 1 — As Águas Claras");
    }

    void startPhase2() {
        double spd = (diff == Diff.SABIO) ? 1.3 : 2.3;
        enemies.clear();
        corals.clear();
        camX  = 0;
        heroX = 80;
        heroY = H / 2.0;
        // Inimigos
        enemies.add(new double[]{ 850,  H * .40, spd, 55,  H * .40, 2 });
        enemies.add(new double[]{ 1750, H * .50, spd, 55,  H * .50, 2 });
        enemies.add(new double[]{ 2650, H * .40, spd, 60,  H * .40, 0 });
        // Corais — pares teto/chão em worldX
        double[] coralX = {380, 620, 860, 1100, 1340, 1580, 1820, 2060, 2300, 2540};
        for (int i = 0; i < coralX.length; i++) {
            double topH = 55 + (i % 3) * 28;
            double botH = 50 + ((i + 1) % 3) * 28;
            corals.add(new double[]{ coralX[i], 0,      70, topH });  // teto
            corals.add(new double[]{ coralX[i], H - botH, 70, botH }); // chão
        }
        // Easter egg
        chestWorldX = 1480;
        chestY      = H - 110;
        // Tabuleta 2
        tab2X = PHASE_LEN - 280;
        tab2Y = H / 2.0 - TAB_H / 2;
        state = State.PHASE2;
        showAlert("🪸 Fase 2 — As Cavernas de Coral");
    }

    void startPhase3() {
        bossX = W - BOSS_W - 100;
        bossY = H / 2.0 - BOSS_H / 2;
        bossHP = BOSS_MAX_HP;
        bubbles.clear();
        beams.clear();
        camX  = 0;
        heroX = 80;
        heroY = H / 2.0 - HERO_H / 2;
        lastBubbleTime = nano + 1_400_000_000L; // entrada legivel antes do primeiro ataque
        state = State.PHASE3;
        showAlert("💀 Fase 3 — O Templo Submerso");
    }

    void goToMenu() {
        state = State.MENU;
        showCredits = false;
    }

    // =========================================================
    // 4. INPUT
    // =========================================================

    /** Processar evento pontual de tecla (pressionada uma vez) */
    void onKey(KeyCode k) {
        switch (state) {
            case MENU     -> handleMenuKey(k);
            case DIALOGUE -> {
                if (k == KeyCode.SPACE || k == KeyCode.ENTER) {
                    if (++dlgLine >= DLG.length) startPhase1();
                }
            }
            case PHASE1, PHASE2, PHASE3 -> {
                if (k == KeyCode.ESCAPE) goToMenu();
            }
            case VICTORY, GAMEOVER -> {
                if (k == KeyCode.SPACE || k == KeyCode.ENTER || k == KeyCode.R)
                    goToMenu();
            }
        }
    }

    void handleMenuKey(KeyCode k) {
        if (showCredits) {
            if (k == KeyCode.SPACE || k == KeyCode.ENTER || k == KeyCode.ESCAPE)
                showCredits = false;
            return;
        }
        if (k == KeyCode.UP   || k == KeyCode.W) menuSel = (menuSel - 1 + 4) % 4;
        if (k == KeyCode.DOWN || k == KeyCode.S) menuSel = (menuSel + 1) % 4;
        if (k == KeyCode.ENTER || k == KeyCode.SPACE) {
            switch (menuSel) {
                case 0 -> diff = Diff.SABIO;
                case 1 -> diff = Diff.IRA;
                case 2 -> { reset(); dlgLine = 0; state = State.DIALOGUE; }
                case 3 -> showCredits = true;
            }
        }
    }

    /** Verifica se alguma das teclas fornecidas está pressionada */
    boolean key(KeyCode... codes) {
        for (KeyCode c : codes) if (keys.contains(c)) return true;
        return false;
    }

    // =========================================================
    // 5. UPDATE — Lógica de Jogo
    // =========================================================

    void update() {
        switch (state) {
            case PHASE1 -> updatePhase1();
            case PHASE2 -> updatePhase2();
            case PHASE3 -> updatePhase3();
        }
        // Partículas: mover e decrementar vida
        particles.removeIf(p -> {
            p[0] += p[2]; p[1] += p[3];
            p[4] -= 0.03;
            return p[4] <= 0;
        });
        // Expirar invencibilidade após 1.5s
        if (invincible && nano - invStart > 2_400_000_000L)
            invincible = false;
    }

    // --- Movimento do Herói (comum às 3 fases) ---

    /** Move o herói com WASD/Setas. Atualiza facingRight para flip de sprite. */
    void moveHero(double speed) {
        if (key(KeyCode.LEFT,  KeyCode.A)) { heroX -= speed; facingRight = false; }
        if (key(KeyCode.RIGHT, KeyCode.D)) { heroX += speed; facingRight = true;  }
        if (key(KeyCode.UP,    KeyCode.W))   heroY -= speed;
        if (key(KeyCode.DOWN,  KeyCode.S))   heroY += speed;
    }

    // --- Fase 1 ---

    void updatePhase1() {
        double speed = (diff == Diff.SABIO) ? 4.5 : 6.0;
        moveHero(speed);

        // Câmera segue herói — ativa quando herói passa 35% da tela
        camX = clamp(heroX - W * 0.35, 0, PHASE_LEN - W);

        // Conter herói nos limites do mundo visível
        heroX = clamp(heroX, 25, PHASE_LEN - HERO_W - 25);
        heroY = clamp(heroY, 30, H - HERO_H - 30);
        double hx = heroX - camX;

        // Disparo de feixe (ESPAÇO)
        if (key(KeyCode.SPACE) && nano - lastShotTime > 400_000_000L) {
            spawnBeam();
            lastShotTime = nano;
        }

        updateBeamsScroll();
        updateEnemiesOscillation();
        checkEnemyCollision();

        // Coletar Tabuleta 1
        if (tab1alive) {
            double tabScreenX = tab1X - camX;
            if (rectsHit(hx, heroY, HERO_W, HERO_H, tabScreenX, tab1Y, TAB_W, TAB_H)) {
                tab1alive = false;
                tabs++;
                spawnBurst(tabScreenX + TAB_W / 2, tab1Y + TAB_H / 2, Color.GOLD);
                showAlert("✦ 1ª Tabuleta da Sabedoria coletada! ✦");
            }
        }

        // Transição para Fase 2 ao chegar no fim do mundo
        if (heroX > PHASE_LEN - 150 && tabs >= 1) startPhase2();
    }

    // --- Fase 2 ---

    void updatePhase2() {
        double speed = (diff == Diff.SABIO) ? 4.5 : 6.0;
        moveHero(speed);

        camX = clamp(heroX - W * 0.35, 0, PHASE_LEN - W);

        // Conter herói (teto/chão mais restrito por causa dos corais)
        heroX = clamp(heroX, 25, PHASE_LEN - HERO_W - 25);
        heroY = clamp(heroY, 55, H - HERO_H - 55);
        double hx = heroX - camX;

        // Colisão com corais (obstáculos sólidos — causa dano e empurrão)
        for (double[] c : corals) {
            double cx = c[0] - camX, cy = c[1], cw = c[2], ch = c[3];
            if (cx < -80 || cx > W + 80) continue; // fora da tela — pular
            if (rectsHit(hx, heroY, HERO_W, HERO_H, cx, cy, cw, ch)) {
                // Empurrar herói para fora do coral
                if (cy == 0) heroY = cy + ch + 2;   // colidiu com teto
                else         heroY = cy - HERO_H - 2; // colidiu com chão
                damageHero(hx + HERO_W / 2, heroY + HERO_H / 2, Color.ORANGERED);
            }
        }

        // Disparo
        if (key(KeyCode.SPACE) && nano - lastShotTime > 400_000_000L) {
            spawnBeam();
            lastShotTime = nano;
        }

        updateBeamsScroll();
        updateEnemiesOscillation();
        checkEnemyCollision();

        // Easter Egg — pressionar ESPAÇO perto do baú
        double chestScreenX = chestWorldX - camX;
        if (!easterFound && key(KeyCode.SPACE)
                && rectsHit(hx, heroY, HERO_W + 50, HERO_H + 50,
                             chestScreenX - 30, chestY - 30, 120, 100)) {
            easterFound    = true;
            easterShowTime = nano;
            spawnBurst(chestScreenX + 30, chestY + 22, Color.GOLD);
        }

        // Coletar Tabuleta 2
        if (tab2alive) {
            double tabScreenX = tab2X - camX;
            if (rectsHit(hx, heroY, HERO_W, HERO_H, tabScreenX, tab2Y, TAB_W, TAB_H)) {
                tab2alive = false;
                tabs++;
                spawnBurst(tabScreenX + TAB_W / 2, tab2Y + TAB_H / 2, Color.GOLD);
                showAlert("✦ 2ª Tabuleta da Sabedoria coletada! ✦");
            }
        }

        if (heroX > PHASE_LEN - 150 && tabs >= 2) startPhase3();
    }

    // --- Fase 3: Boss Fight ---

    void updatePhase3() {
        double speed = (diff == Diff.SABIO) ? 4.5 : 6.0;
        moveHero(speed);

        // Herói confinado à arena (sem câmera — tela fixa)
        heroX = clamp(heroX, 15, W - HERO_W - 15);
        heroY = clamp(heroY, 15, H - HERO_H - 15);

        // Disparo com direção ao boss (feixe teleguiado)
        if (key(KeyCode.SPACE) && nano - lastShotTime > 350_000_000L) {
            spawnBeamTowardBoss();
            lastShotTime = nano;
        }

        // Mover feixes e detectar acerto no boss
        Iterator<double[]> bit = beams.iterator();
        while (bit.hasNext()) {
            double[] b = bit.next();
            b[0] += b[2];
            b[1] += b[3];
            if (b[0] < 0 || b[0] > W || b[1] < 0 || b[1] > H) {
                bit.remove();
                continue;
            }
            // Hit no boss
            if (rectsHit(b[0] - 8, b[1] - 8, 16, 16, bossX, bossY, BOSS_W, BOSS_H)) {
                bit.remove();
                bossHP--;
                spawnBurst(bossX + BOSS_W / 2, bossY + BOSS_H / 2, Color.CYAN);
                if (bossHP <= 0) {
                    tabs++;
                    spawnBurst(bossX + BOSS_W / 2, bossY + BOSS_H / 2, Color.GOLD);
                    state = State.VICTORY;
                }
            }
        }

        // Boss dispara bolhas em leque
        long bubbleInterval = (diff == Diff.SABIO) ? 2_200_000_000L : 1_200_000_000L;
        if (nano - lastBubbleTime > bubbleInterval) {
            lastBubbleTime = nano;
            int   count    = (diff == Diff.SABIO) ? 2 : 4;
            double spread  = Math.PI * 0.7;
            for (int i = 0; i < count; i++) {
                double angle = Math.PI * 0.8 + i * (spread / Math.max(count - 1, 1));
                double bspd  = (diff == Diff.SABIO) ? 4.0 : 6.0;
                bubbles.add(new double[]{
                    bossX, bossY + BOSS_H / 2,
                    Math.cos(angle) * bspd, Math.sin(angle) * bspd
                });
            }
        }

        // Mover bolhas e checar colisão com herói
        Iterator<double[]> buit = bubbles.iterator();
        while (buit.hasNext()) {
            double[] b = buit.next();
            b[0] += b[2];
            b[1] += b[3];
            if (b[0] < -40 || b[0] > W + 40 || b[1] < -40 || b[1] > H + 40) {
                buit.remove();
                continue;
            }
            if (!invincible && rectsHit(heroX, heroY, HERO_W, HERO_H, b[0] - 12, b[1] - 12, 24, 24)) {
                buit.remove();
                damageHero(heroX + HERO_W / 2, heroY + HERO_H / 2, Color.PURPLE);
            }
        }
    }

    // --- Helpers de Update ---

    /** Spawna feixe em coordenadas de mundo nas fases com scroll. */
    void spawnBeam() {
        double bx = facingRight ? heroX + HERO_W : heroX;
        double by = heroY + HERO_H / 2;
        double vx = facingRight ? 13 : -13;
        beams.add(new double[]{ bx, by, vx, 0 });
    }

    /** Spawna feixe em direção ao centro do boss (fase 3) */
    void spawnBeamTowardBoss() {
        double bx = heroX + HERO_W / 2;
        double by = heroY + HERO_H / 2;
        double dx = (bossX + BOSS_W / 2) - bx;
        double dy = (bossY + BOSS_H / 2) - by;
        double len = Math.sqrt(dx * dx + dy * dy);
        if (len == 0) return;
        beams.add(new double[]{ bx, by, dx / len * 11, dy / len * 11 });
    }

    /**
     * Atualiza feixes nas fases com scroll (Fase 1 e 2).
     * Feixes usam coordenadas de MUNDO. Remove ao sair do mundo ou acertar inimigo.
     */
    void updateBeamsScroll() {
        Iterator<double[]> it = beams.iterator();
        while (it.hasNext()) {
            double[] b = it.next();
            b[0] += b[2];
            if (b[0] < 0 || b[0] > PHASE_LEN) { it.remove(); continue; }

            // Verificar acerto em inimigos
            boolean hit = false;
            for (Iterator<double[]> enemyIt = enemies.iterator(); enemyIt.hasNext();) {
                double[] e = enemyIt.next();
                if (rectsHit(b[0] - 6, b[1] - 6, 12, 12, e[0], e[1], ENEMY_W, ENEMY_H)) {
                    spawnBurst(b[0] - camX, b[1], Color.AQUAMARINE);
                    enemyIt.remove(); // ataque deve abrir caminho, como em um platformer classico
                    hit = true;
                    break;
                }
            }
            if (hit) it.remove();
        }
    }

    /**
     * Movimento senoidal dos inimigos. Cada inimigo tem fase diferente
     * (baseada em worldX) para não moverem sincronizados.
     */
    void updateEnemiesOscillation() {
        double t = nano / 1_000_000_000.0;
        for (double[] e : enemies) {
            // e[1]=screenY | e[2]=speed | e[3]=amplitude | e[4]=baseY | e[0]=worldX(como phase)
            e[1] = e[4] + Math.sin(t * e[2] + e[0] * 0.009) * e[3];
        }
    }

    /** Verifica colisão do herói com todos os inimigos e aplica dano */
    void checkEnemyCollision() {
        if (invincible) return;
        for (Iterator<double[]> it = enemies.iterator(); it.hasNext();) {
            double[] e = it.next();
            double ex = e[0] - camX;
            double hx = heroX - camX;
            if (rectsHit(hx, heroY, HERO_W, HERO_H, ex, e[1], ENEMY_W, ENEMY_H)) {
                it.remove(); // contato remove a ameaca e evita dano repetido injusto
                damageHero(hx + HERO_W / 2, heroY + HERO_H / 2, Color.RED);
                break;
            }
        }
    }

    /** Aplica dano ao herói e uma janela generosa para reposicionamento. */
    void damageHero(double px, double py, Color c) {
        if (invincible) return;
        heroHP--;
        invincible = true;
        invStart   = nano;
        spawnBurst(px, py, c);
        if (heroHP <= 0) state = State.GAMEOVER;
    }

    // =========================================================
    // 6. RENDER — Desenho
    // =========================================================

    void render(GraphicsContext gc) {
        gc.clearRect(0, 0, W, H);
        switch (state) {
            case MENU     -> renderMenu(gc);
            case DIALOGUE -> renderDialogue(gc);
            case PHASE1   -> renderPhase1(gc);
            case PHASE2   -> renderPhase2(gc);
            case PHASE3   -> renderPhase3(gc);
            case VICTORY  -> renderVictory(gc);
            case GAMEOVER -> renderGameOver(gc);
        }
    }

    // --- Menu ---

    void renderMenu(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        drawGradientBg(gc, "#0a0e2a", "#0d3b6e", "#1a6b8a");

        // Bolhas animadas de fundo
        gc.setFill(Color.rgb(100, 200, 255, 0.11));
        for (int i = 0; i < 24; i++) {
            double bx = (i * 83 + Math.sin(t * 0.38 + i) * 38 + W * 4) % W;
            double by = (H - (t * (20 + i % 7) + i * 68) % (H + 80));
            double bs = 7 + (i % 5) * 6;
            gc.fillOval(bx, by, bs, bs);
        }

        gc.setTextAlign(TextAlignment.CENTER);
        gc.setTextBaseline(VPos.CENTER);

        // Título principal
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 58));
        gc.setFill(Color.rgb(0, 160, 255, 0.25));
        gc.fillText("✦ AS ÁGUAS DE APSU ✦", W / 2.0 + 3, 125);
        gc.setFill(Color.web("#ffd700"));
        gc.fillText("✦ AS ÁGUAS DE APSU ✦", W / 2.0, 122);

        gc.setFont(Font.font("Serif", FontWeight.BOLD, 26));
        gc.setFill(Color.web("#90d8ff"));
        gc.fillText("A Lenda dos Apkallu", W / 2.0, 178);

        if (showCredits) { renderCredits(gc); return; }

        // Opções do menu
        String[] opts = {
            "◉  Sábio  (Fácil)  —  5 ❤   Inimigos lentos",
            "◉  Ira de Enki  (Difícil)  —  3 ❤   Inimigos rápidos",
            "▶  INICIAR JOGO",
            "✦  Créditos Mitológicos"
        };
        double[] ys = { 292, 348, 438, 516 };

        for (int i = 0; i < opts.length; i++) {
            boolean selected = (i == menuSel);
            boolean active   = (i == 0 && diff == Diff.SABIO) || (i == 1 && diff == Diff.IRA);

            if (selected) {
                gc.setFill(Color.rgb(0, 140, 255, 0.22));
                gc.fillRoundRect(W / 2.0 - 310, ys[i] - 28, 620, 54, 16, 16);
            }
            gc.setFont(Font.font("Serif", selected ? FontWeight.BOLD : FontWeight.NORMAL,
                                 selected ? 28 : 23));
            gc.setFill(selected ? Color.web("#ffd700")
                                : active ? Color.web("#5fffa0")
                                         : Color.web("#88c0e0"));
            gc.fillText(opts[i], W / 2.0, ys[i]);
        }

        // Rodapé
        gc.setFont(Font.font("Serif", 15));
        gc.setFill(Color.web("#3a7090"));
        gc.fillText("↑ ↓  selecionar   •   ENTER confirmar   •   ESPAÇO = atirar/interagir   •   ESC = menu",
                    W / 2.0, H - 26);
    }

    void renderCredits(GraphicsContext gc) {
        gc.setFill(Color.rgb(4, 12, 38, 0.92));
        gc.fillRoundRect(W / 2.0 - 360, 200, 720, 370, 22, 22);
        gc.setStroke(Color.web("#2060cc"));
        gc.setLineWidth(2);
        gc.strokeRoundRect(W / 2.0 - 360, 200, 720, 370, 22, 22);

        gc.setTextAlign(TextAlignment.CENTER);
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 24));
        gc.setFill(Color.web("#ffd700"));
        gc.fillText("Créditos Mitológicos Mesopotâmicos", W / 2.0, 242);

        gc.setFont(Font.font("Serif", 18));
        gc.setFill(Color.web("#a0d4ff"));
        String[] lines = {
            "Adapa — Herói Apkallu, sábio dos oceanos primordiais",
            "Enki — Deus sumérico da sabedoria, das águas e da criação",
            "Kullullû — O Apkallu corrompido, guardião das trevas",
            "Apsu — Oceano primordial masculino da cosmogonia mesopotâmica",
            "Tabuletas — Registros cuneiformes de Nippur (~2100 a.C.)",
            "Tartaruga Ancestral — Artefato fóssil dos templos de Eridu"
        };
        for (int i = 0; i < lines.length; i++)
            gc.fillText(lines[i], W / 2.0, 290 + i * 40);

        gc.setFill(Color.web("#ffd700"));
        gc.setFont(Font.font("Serif", 16));
        gc.fillText("[ ESPAÇO / ENTER para voltar ]", W / 2.0, 552);
    }

    // --- Diálogo ---

    void renderDialogue(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        drawGradientBg(gc, "#040c18", "#091c38", "#0c2a4c");

        // Bolhas decorativas no fundo
        gc.setFill(Color.rgb(0, 90, 200, 0.10));
        for (int i = 0; i < 16; i++)
            gc.fillOval(i * 86 + Math.sin(t * 0.5 + i) * 20,
                        H - 80 + Math.cos(t * 0.6 + i) * 26,
                        16 + (i % 4) * 8, 16 + (i % 4) * 8);

        // Avatar Enki (PNG ou fallback)
        double avatarY = H / 2.0 - 160;
        if (imgNpc != null) {
            gc.drawImage(imgNpc, 35, avatarY, 230, 320);
        } else {
            drawNpcFallback(gc, 35, avatarY);
        }

        // Caixa de diálogo
        gc.setFill(Color.rgb(4, 14, 36, 0.92));
        gc.fillRoundRect(295, H / 2.0 - 150, W - 370, 290, 26, 26);
        gc.setStroke(Color.web("#1a50c0"));
        gc.setLineWidth(2);
        gc.strokeRoundRect(295, H / 2.0 - 150, W - 370, 290, 26, 26);

        // Nome do personagem
        gc.setFill(Color.web("#70b8ff"));
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 22));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.fillText("Enki — Senhor das Águas Primordiais:", 320, H / 2.0 - 118);

        // Texto do diálogo com wrap automático
        gc.setFill(Color.WHITE);
        gc.setFont(Font.font("Serif", 21));
        if (dlgLine < DLG.length)
            wrapText(gc, DLG[dlgLine], 320, H / 2.0 - 80, W - 490, 34);

        // Indicador de progresso (pontos)
        for (int i = 0; i < DLG.length; i++) {
            gc.setFill(i < dlgLine ? Color.web("#ffd700") : Color.web("#1c2c50"));
            gc.fillOval(W / 2.0 - DLG.length * 15 + i * 30, H / 2.0 + 118, 15, 15);
        }

        gc.setTextAlign(TextAlignment.CENTER);
        gc.setFill(Color.web("#ffd700"));
        gc.setFont(Font.font("Serif", 16));
        gc.fillText("[ ESPAÇO para continuar ]", W / 2.0, H / 2.0 + 158);
    }

    // --- Fases ---

    void renderPhase1(GraphicsContext gc) {
        if (imgBg1 != null) gc.drawImage(imgBg1, 0, 0, W, H);
        else drawOceanBg(gc, "#0d4a8a", "#1a7fc4", "#2aa8e0", true);

        drawPhase1Decorations(gc);

        // Tabuleta 1
        if (tab1alive) drawTablet(gc, tab1X - camX, tab1Y);

        // Portal de transição de fase
        drawPortal(gc, PHASE_LEN - 100 - camX);

        for (double[] e : enemies) drawEnemy(gc, e[0] - camX, e[1], (int) e[5]);
        drawBeamsScroll(gc);
        drawHero(gc, heroX - camX, heroY);
        drawParticles(gc);
        renderHUD(gc, "Fase 1 — As Águas Claras");
        renderAlert(gc);
    }

    void renderPhase2(GraphicsContext gc) {
        if (imgBg2 != null) gc.drawImage(imgBg2, 0, 0, W, H);
        else drawOceanBg(gc, "#050f18", "#0a2232", "#0d3448", false);

        // Corais (apenas os visíveis na tela)
        for (double[] c : corals) {
            double cx = c[0] - camX;
            if (cx < -90 || cx > W + 90) continue;
            drawCoral(gc, cx, c[1], c[2], c[3], c[1] == 0);
        }

        // Easter Egg — baú
        drawChest(gc, chestWorldX - camX, chestY);

        // Easter Egg popup
        if (easterFound && nano - easterShowTime < 6_000_000_000L)
            renderEasterEgg(gc);

        if (tab2alive) drawTablet(gc, tab2X - camX, tab2Y);
        drawPortal(gc, PHASE_LEN - 100 - camX);

        for (double[] e : enemies) drawEnemy(gc, e[0] - camX, e[1], (int) e[5]);
        drawBeamsScroll(gc);
        drawHero(gc, heroX - camX, heroY);
        drawParticles(gc);
        renderHUD(gc, "Fase 2 — As Cavernas de Coral");
        renderAlert(gc);
    }

    void renderPhase3(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        if (imgBg3 != null) gc.drawImage(imgBg3, 0, 0, W, H);
        else drawTempleBg(gc);

        drawTempleColumns(gc);

        // Bolhas do boss
        for (double[] b : bubbles) {
            double pulse = 13 + Math.sin(t * 7 + b[0]) * 3;
            gc.setFill(Color.rgb(120, 0, 200, 0.70));
            gc.fillOval(b[0] - pulse / 2, b[1] - pulse / 2, pulse, pulse);
            gc.setFill(Color.rgb(70, 0, 160, 0.22));
            gc.fillOval(b[0] - pulse, b[1] - pulse, pulse * 2, pulse * 2);
        }

        drawBossHPBar(gc);
        drawBoss(gc, bossX, bossY);
        drawBeams(gc);
        drawHero(gc, heroX, heroY);
        drawParticles(gc);
        renderHUD(gc, "Fase 3 — O Templo Submerso");
        renderAlert(gc);
    }

    // --- Telas de Fim ---

    void renderVictory(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        drawGradientBg(gc, "#061206", "#0e2a10", "#184818");
        drawParticles(gc);

        // Partículas orbitais douradas
        gc.setFill(Color.rgb(255, 215, 0, 0.55));
        for (int i = 0; i < 22; i++) {
            gc.fillOval(W / 2.0 + Math.cos(t * 0.55 + i * 0.285) * (195 + i * 11),
                        H / 2.0 + Math.sin(t * 0.75 + i * 0.285) * (130 + i * 9), 10, 10);
        }

        gc.setTextAlign(TextAlignment.CENTER);
        gc.setTextBaseline(VPos.CENTER);

        gc.setFont(Font.font("Serif", FontWeight.BOLD, 76));
        gc.setFill(Color.web("#ffd700"));
        gc.fillText("✦ VITÓRIA ✦", W / 2.0, 205);

        gc.setFont(Font.font("Serif", 28));
        gc.setFill(Color.web("#88ffaa"));
        gc.fillText("Adapa recuperou as 3 Tabuletas da Sabedoria!", W / 2.0, 312);
        gc.fillText("Kullullû foi derrotado. O Apsu está purificado.", W / 2.0, 358);
        gc.setFill(Color.web("#a0ffcc"));
        gc.fillText("A luz da sabedoria prevalece sobre as trevas do abismo.", W / 2.0, 404);

        gc.setFont(Font.font("Serif", FontWeight.BOLD, 26));
        gc.setFill(Color.web("#ffd700"));
        gc.fillText("[ ESPAÇO / ENTER — Voltar ao Menu ]", W / 2.0, H - 90);
    }

    void renderGameOver(GraphicsContext gc) {
        drawGradientBg(gc, "#120408", "#28080e", "#3e0a14");
        drawParticles(gc);

        gc.setTextAlign(TextAlignment.CENTER);
        gc.setTextBaseline(VPos.CENTER);

        gc.setFont(Font.font("Serif", FontWeight.BOLD, 84));
        gc.setFill(Color.web("#ff2828"));
        gc.fillText("GAME OVER", W / 2.0, 230);

        gc.setFont(Font.font("Serif", 26));
        gc.setFill(Color.web("#ff9090"));
        gc.fillText("Adapa caiu nas profundezas do Apsu...", W / 2.0, 344);
        gc.fillText("As Tabuletas permanecem perdidas nas trevas.", W / 2.0, 388);

        gc.setFill(Color.web("#ffd700"));
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 24));
        gc.fillText("Tabuletas coletadas: " + tabs + " / 3", W / 2.0, 440);

        gc.setFont(Font.font("Serif", FontWeight.BOLD, 26));
        gc.fillText("[ R / ESPAÇO / ENTER — Tentar Novamente ]", W / 2.0, H - 90);
    }

    // --- HUD e UI ---

    void renderHUD(GraphicsContext gc, String phaseName) {
        // Painel esquerdo (vida + tabuletas + fase)
        gc.setFill(Color.rgb(0, 4, 16, 0.74));
        gc.fillRoundRect(10, 10, 306, 108, 14, 14);
        gc.setStroke(Color.rgb(0, 130, 255, 0.30));
        gc.setLineWidth(1.5);
        gc.strokeRoundRect(10, 10, 306, 108, 14, 14);

        gc.setTextAlign(TextAlignment.LEFT);
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 17));
        gc.setFill(Color.web("#88ccff"));
        gc.fillText("Vida:", 24, 38);

        int maxHP = (diff == Diff.SABIO) ? 5 : 3;
        for (int i = 0; i < maxHP; i++) {
            gc.setFill(i < heroHP ? Color.web("#ff2040") : Color.web("#252540"));
            gc.setFont(Font.font("Serif", 20));
            gc.fillText("❤", 72 + i * 30, 40);
        }

        gc.setFont(Font.font("Serif", FontWeight.BOLD, 17));
        gc.setFill(Color.web("#88ccff"));
        gc.fillText("Tabuletas:", 24, 66);
        gc.setFill(Color.web("#ffd700"));
        gc.fillText(tabs + " / 3", 130, 66);

        gc.setFill(Color.web("#6094c0"));
        gc.setFont(Font.font("Serif", 14));
        gc.fillText(phaseName, 24, 94);

        // Badge de dificuldade (canto superior direito)
        gc.setFill(Color.rgb(0, 4, 16, 0.74));
        gc.fillRoundRect(W - 232, 10, 222, 46, 12, 12);
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 16));
        gc.setFill((diff == Diff.SABIO) ? Color.web("#40ff88") : Color.web("#ff4444"));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText((diff == Diff.SABIO) ? "⚡ Modo: Sábio" : "🔥 Ira de Enki", W - 121, 37);
    }

    void renderAlert(GraphicsContext gc) {
        if (alertMsg.isEmpty()) return;
        long elapsed = nano - alertTime;
        if (elapsed > 3_200_000_000L) { alertMsg = ""; return; }

        // Fade out nos últimos 600ms
        double alpha = Math.min(1.0, (3_200_000_000L - elapsed) / 600_000_000.0);
        gc.setFill(Color.rgb(0, 6, 24, alpha * 0.88));
        gc.fillRoundRect(W / 2.0 - 320, H - 92, 640, 58, 12, 12);
        gc.setFill(Color.rgb(255, 215, 0, alpha));
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 22));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText(alertMsg, W / 2.0, H - 56);
    }

    void renderEasterEgg(GraphicsContext gc) {
        gc.setFill(Color.rgb(4, 14, 44, 0.94));
        gc.fillRoundRect(W / 2.0 - 350, H / 2.0 - 78, 700, 136, 18, 18);
        gc.setStroke(Color.web("#ffd700"));
        gc.setLineWidth(2);
        gc.strokeRoundRect(W / 2.0 - 350, H / 2.0 - 78, 700, 136, 18, 18);

        gc.setTextAlign(TextAlignment.CENTER);
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 23));
        gc.setFill(Color.web("#ffd700"));
        gc.fillText("🐢  Easter Egg Descoberto!", W / 2.0, H / 2.0 - 38);

        gc.setFont(Font.font("Serif", 20));
        gc.setFill(Color.web("#c0e4ff"));
        gc.fillText("Você encontrou o fóssil da Tartaruga Ancestral de 4.000 a.C.!", W / 2.0, H / 2.0 + 6);

        gc.setFont(Font.font("Serif", 15));
        gc.setFill(Color.web("#7090b0"));
        gc.fillText("Artefato registrado nas tabuletas de Nippur — Século XXI a.C.", W / 2.0, H / 2.0 + 40);
    }

    // =========================================================
    // 7. DRAW HELPERS — Desenho de entidades e cenário
    // =========================================================

    /** Herói Adapa — usa PNG ou fallback geométrico. Pisca durante invencibilidade. */
    void drawHero(GraphicsContext gc, double x, double y) {
        // Piscar a cada 100ms durante invencibilidade (iframe visual)
        if (invincible && (nano / 100_000_000L) % 2 == 0) return;

        double t = nano / 1_000_000_000.0;

        if (imgHero != null) {
            gc.save();
            if (!facingRight) {
                // Flip horizontal: translada para borda direita, escala -1 no X
                gc.translate(x + HERO_W, y);
                gc.scale(-1, 1);
                gc.drawImage(imgHero, 0, 0, HERO_W, HERO_H);
            } else {
                gc.drawImage(imgHero, x, y, HERO_W, HERO_H);
            }
            gc.restore();
        } else {
            drawHeroFallback(gc, x, y);
        }

        // Aura de energia (anel pulsante)
        gc.setStroke(Color.rgb(60, 160, 255, 0.26));
        gc.setLineWidth(3 + Math.sin(t * 3) * 1.5);
        gc.strokeOval(x - 5, y - 5, HERO_W + 10, HERO_H + 10);
    }

    void drawHeroFallback(GraphicsContext gc, double x, double y) {
        gc.save();
        double ox = x, oy = y;
        if (!facingRight) { gc.translate(x + HERO_W, y); gc.scale(-1, 1); ox = 0; oy = 0; }
        // Cauda
        gc.setFill(Color.web("#208050"));
        gc.fillPolygon(
            new double[]{ ox + 6, ox + HERO_W * .5, ox + HERO_W * .28, ox - 2 },
            new double[]{ oy + HERO_H, oy + HERO_H * .68, oy + HERO_H * .86, oy + HERO_H * .76 }, 4);
        // Corpo
        gc.setFill(Color.web("#34a068"));
        gc.fillRoundRect(ox + HERO_W * .1, oy + HERO_H * .42, HERO_W * .8, HERO_H * .4, 10, 10);
        // Torso com armadura
        gc.setFill(Color.web("#b08860"));
        gc.fillRoundRect(ox + HERO_W * .12, oy + HERO_H * .20, HERO_W * .76, HERO_H * .28, 8, 8);
        // Cabeça
        gc.setFill(Color.web("#c09868"));
        gc.fillOval(ox + HERO_W * .16, oy, HERO_W * .68, HERO_H * .26);
        // Tiara
        gc.setFill(Color.web("#7a5030"));
        gc.fillRect(ox + HERO_W * .18, oy + HERO_H * .04, HERO_W * .64, 6);
        // Olho
        gc.setFill(Color.web("#1c1e3e"));
        gc.fillOval(ox + HERO_W * .54, oy + HERO_H * .08, 8, 8);
        gc.restore();
    }

    /** Boss Kullullû — usa PNG ou fallback geométrico com animação de flutuação */
    void drawBoss(GraphicsContext gc, double x, double y) {
        double t   = nano / 1_000_000_000.0;
        double bob = Math.sin(t * 1.8) * 8;  // flutuação vertical

        if (imgBoss != null) {
            gc.drawImage(imgBoss, x, y + bob, BOSS_W, BOSS_H);
        } else {
            drawBossFallback(gc, x, y + bob);
        }
    }

    void drawBossFallback(GraphicsContext gc, double x, double y) {
        // Aura sombria
        gc.setFill(Color.rgb(80, 0, 120, 0.30));
        gc.fillOval(x - 20, y - 20, BOSS_W + 40, BOSS_H + 40);
        // Cauda
        gc.setFill(Color.web("#300040"));
        gc.fillPolygon(
            new double[]{ x + 8,  x + BOSS_W * .5, x + BOSS_W * .2, x - 8 },
            new double[]{ y + BOSS_H, y + BOSS_H * .68, y + BOSS_H * .86, y + BOSS_H * .76 }, 4);
        // Corpo
        gc.setFill(Color.web("#3e0052"));
        gc.fillRoundRect(x + BOSS_W * .1, y + BOSS_H * .42, BOSS_W * .8, BOSS_H * .4, 12, 12);
        // Torso
        gc.setFill(Color.web("#280034"));
        gc.fillRoundRect(x + BOSS_W * .1, y + BOSS_H * .20, BOSS_W * .8, BOSS_H * .28, 10, 10);
        // Cabeça
        gc.setFill(Color.web("#300044"));
        gc.fillOval(x + BOSS_W * .12, y, BOSS_W * .76, BOSS_H * .26);
        // Olhos vermelhos
        gc.setFill(Color.web("#ff0000"));
        gc.fillOval(x + BOSS_W * .22, y + BOSS_H * .06, 13, 13);
        gc.fillOval(x + BOSS_W * .56, y + BOSS_H * .06, 13, 13);
    }

    void drawBossHPBar(GraphicsContext gc) {
        double bw = 420, bh = 24, bx = W / 2.0 - 210, by = 14;
        // Fundo escuro
        gc.setFill(Color.rgb(0, 0, 0, 0.74));
        gc.fillRoundRect(bx - 8, by - 7, bw + 16, bh + 14, 12, 12);
        gc.setFill(Color.web("#180010"));
        gc.fillRoundRect(bx, by, bw, bh, 6, 6);
        // Barra de HP
        double ratio = bossHP / (double) BOSS_MAX_HP;
        gc.setFill(Color.web("#aa0024"));
        gc.fillRoundRect(bx, by, bw * ratio, bh, 6, 6);
        // Highlight
        gc.setFill(Color.rgb(255, 60, 90, 0.40));
        gc.fillRoundRect(bx, by, bw * ratio * 0.5, bh / 2.0, 6, 6);
        // Texto
        gc.setFill(Color.WHITE);
        gc.setFont(Font.font("Serif", FontWeight.BOLD, 14));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText("Kullullû  " + bossHP + " / " + BOSS_MAX_HP, W / 2.0, by + bh - 4);
    }

    void drawEnemy(GraphicsContext gc, double x, double y, int type) {
        double t = nano / 1_000_000_000.0;
        // Corpo do peixe/caranguejo
        gc.setFill(type == 2 ? Color.web("#0a3a2a") : Color.web("#185030"));
        gc.fillOval(x, y, ENEMY_W, ENEMY_H);
        // Nadadeira/cauda
        gc.fillPolygon(
            new double[]{ x, x - 14, x - 9 },
            new double[]{ y + 10, y + 5, y + 24 }, 3);
        // Olho
        gc.setFill(Color.web("#e04400"));
        gc.fillOval(x + 29, y + 8, 7, 7);
        // Pinças do caranguejo (type 2)
        if (type == 2) {
            gc.setFill(Color.web("#8a3200"));
            gc.fillPolygon(new double[]{ x + 8,  x + 13, x + 18 }, new double[]{ y, y - 12, y }, 3);
            gc.fillPolygon(new double[]{ x + 20, x + 25, x + 32 }, new double[]{ y, y - 14, y }, 3);
        }
        // Aura suave pulsante
        gc.setFill(Color.rgb(0, 190, 70, 0.12 + Math.sin(t * 4 + x * 0.01) * 0.06));
        gc.fillOval(x - 6, y - 5, ENEMY_W + 12, ENEMY_H + 10);
    }

    void drawTablet(GraphicsContext gc, double x, double y) {
        double t = nano / 1_000_000_000.0;
        double glow = 3 + Math.sin(t * 4) * 2;
        // Brilho dourado ao redor
        gc.setFill(Color.rgb(255, 220, 0, 0.28));
        gc.fillOval(x - glow * 2.5, y - glow * 2.5, TAB_W + glow * 5, TAB_H + glow * 5);
        // Tabuleta de argila
        gc.setFill(Color.web("#c09848"));
        gc.fillRoundRect(x, y, TAB_W, TAB_H, 5, 5);
        gc.setFill(Color.web("#a07830"));
        gc.fillRoundRect(x + 2, y + 2, TAB_W - 4, TAB_H - 4, 4, 4);
        // Linhas de cuneiforme
        gc.setStroke(Color.web("#ffd700"));
        gc.setLineWidth(1.2);
        for (int i = 0; i < 5; i++)
            gc.strokeLine(x + 5, y + 7 + i * 7, x + TAB_W - 5, y + 7 + i * 7);
    }

    void drawPortal(GraphicsContext gc, double px) {
        if (px < -90 || px > W + 90) return;
        double t = nano / 1_000_000_000.0;
        double pulse = 0.18 + Math.sin(t * 3) * 0.07;
        gc.setFill(Color.rgb(0, 140, 255, pulse));
        gc.fillOval(px - 32, H / 2.0 - 55, 84, 84);
        gc.setStroke(Color.web("#40d8ff"));
        gc.setLineWidth(3);
        gc.strokeOval(px - 32, H / 2.0 - 55, 84, 84);
        gc.setFill(Color.web("#90ffff"));
        gc.setFont(Font.font("Serif", 13));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText("→ Avançar", px + 10, H / 2.0 + 46);
    }

    void drawChest(GraphicsContext gc, double x, double y) {
        if (x < -90 || x > W + 90) return;
        double t = nano / 1_000_000_000.0;
        if (!easterFound) {
            // Brilho de "item especial"
            gc.setFill(Color.rgb(255, 200, 0, 0.14 + Math.sin(t * 2.2) * 0.06));
            gc.fillOval(x - 22, y - 22, 104, 90);
        }
        // Baú
        gc.setFill(easterFound ? Color.web("#4a2e14") : Color.web("#7a5018"));
        gc.fillRoundRect(x, y, 60, 44, 6, 6);
        gc.setFill(easterFound ? Color.web("#382210") : Color.web("#b8901c"));
        gc.fillRect(x, y, 60, 18);
        // Fechadura
        gc.setFill(Color.web("#ffd700"));
        gc.fillOval(x + 24, y + 12, 12, 12);
        // Dica de interação
        if (!easterFound) {
            gc.setFill(Color.web("#ffd700"));
            gc.setFont(Font.font("Serif", 13));
            gc.setTextAlign(TextAlignment.CENTER);
            gc.fillText("[ESPAÇO]", x + 30, y - 8);
        }
    }

    void drawCoral(GraphicsContext gc, double x, double y, double w, double h, boolean isTop) {
        // Rocha base
        gc.setFill(Color.web("#162e3a"));
        gc.fillRect(x, y, w, h);
        // Pontas de coral vermelhas
        gc.setFill(Color.web("#b83030"));
        int count = (int) (w / 16);
        for (int i = 0; i < count; i++) {
            double cw2 = 8, ch2 = 16 + (i % 3) * 12;
            double cx2 = x + i * 16 + 4;
            if (isTop) gc.fillRoundRect(cx2, y + h - ch2, cw2, ch2, 3, 3);
            else       gc.fillRoundRect(cx2, y, cw2, ch2, 3, 3);
        }
    }

    void drawBeams(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        for (double[] b : beams) {
            drawBeam(gc, b[0], b[1], t);
        }
    }

    /** Renderiza os projeteis de fases com camera: mundo -> tela. */
    void drawBeamsScroll(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        for (double[] b : beams) {
            drawBeam(gc, b[0] - camX, b[1], t);
        }
    }

    void drawBeam(GraphicsContext gc, double x, double y, double t) {
        double g = 9 + Math.sin(t * 20) * 2;
        // Halo externo
        gc.setFill(Color.rgb(100, 200, 255, 0.24));
        gc.fillOval(x - g, y - g, g * 2, g * 2);
        // Núcleo brilhante
        gc.setFill(Color.web("#b0f0ff"));
        gc.fillOval(x - 5, y - 5, 10, 10);
        gc.setFill(Color.WHITE);
        gc.fillOval(x - 2, y - 2, 4, 4);
    }

    void drawParticles(GraphicsContext gc) {
        for (double[] p : particles) {
            gc.setFill(Color.rgb(
                (int) (p[5] * 255), (int) (p[6] * 255), (int) (p[7] * 255),
                Math.max(0, p[4])   // alpha = life
            ));
            gc.fillOval(p[0] - 4, p[1] - 4, 8, 8);
        }
    }

    void drawPhase1Decorations(GraphicsContext gc) {
        double t = nano / 1_000_000_000.0;
        // Bolhas decorativas com parallax leve
        gc.setFill(Color.rgb(140, 220, 255, 0.16));
        for (int i = 0; i < 14; i++) {
            double bx = (i * 107 - camX * 0.22 + Math.sin(t + i) * 24 + W * 6) % W;
            double by = (t * (16 + i % 6) + i * 60) % H;
            gc.fillOval(bx, by, 5 + (i % 4) * 6, 5 + (i % 4) * 6);
        }
        // Algas no fundo com parallax
        gc.setFill(Color.web("#145028"));
        for (int i = 0; i < 16; i++) {
            double ax = (i * 94 - (camX * 0.5)) % (W + 100);
            if (ax < -20 || ax > W + 20) continue;
            gc.fillRoundRect(ax, H - 52, 11, 52, 5, 5);
            gc.fillRoundRect(ax + 8, H - 40, 10, 40, 5, 5);
        }
    }

    void drawTempleColumns(GraphicsContext gc) {
        int[] colX = { 140, 350, 640, 900, 1120 };
        for (int cx : colX) {
            gc.setFill(Color.web("#1c0c30"));
            gc.fillRect(cx, 0, 44, H);
            gc.setFill(Color.web("#2a1444"));
            gc.fillRect(cx + 6, 0, 14, H);
            // Capitel e base
            gc.setFill(Color.web("#381c58"));
            gc.fillRect(cx - 10, 0, 64, 42);
            gc.fillRect(cx - 10, H - 42, 64, 42);
        }
    }

    void drawNpcFallback(GraphicsContext gc, double x, double y) {
        // Veste
        gc.setFill(Color.web("#1a3c7a"));
        gc.fillRoundRect(x + 60, y + 68, 155, 240, 18, 18);
        // Cabeça
        gc.setFill(Color.web("#c8a870"));
        gc.fillOval(x + 78, y, 120, 80);
        // Barba
        gc.setFill(Color.web("#c8b880"));
        gc.fillRoundRect(x + 85, y + 54, 100, 32, 10, 10);
        // Olhos
        gc.setFill(Color.web("#1a3060"));
        gc.fillOval(x + 97, y + 26, 12, 12);
        gc.fillOval(x + 128, y + 26, 12, 12);
        // Ornamentos
        gc.setStroke(Color.web("#3888ff"));
        gc.setLineWidth(2);
        for (int i = 0; i < 4; i++) gc.strokeLine(x + 44, y + 158 + i * 24, x + 248, y + 158 + i * 24);
    }

    // =========================================================
    // UTILITÁRIOS
    // =========================================================

    /** Background com gradiente vertical de 3 cores */
    void drawGradientBg(GraphicsContext gc, String top, String mid, String bot) {
        gc.setFill(new LinearGradient(0, 0, 0, 1, true, CycleMethod.NO_CYCLE,
                new Stop(0, Color.web(top)),
                new Stop(0.5, Color.web(mid)),
                new Stop(1, Color.web(bot))));
        gc.fillRect(0, 0, W, H);
    }

    void drawOceanBg(GraphicsContext gc, String top, String mid, String bot, boolean light) {
        drawGradientBg(gc, top, mid, bot);
        double t = nano / 1_000_000_000.0;
        // Raios de luz solar (apenas Fase 1)
        if (light) {
            for (int i = 0; i < 6; i++) {
                gc.setFill(Color.rgb(150, 220, 255, 0.04 + Math.sin(t * 0.3 + i) * 0.02));
                gc.fillPolygon(
                    new double[]{ 90 + i * 210, 60 + i * 180, 250 + i * 180, 300 + i * 180 },
                    new double[]{ 0, 0, H, H }, 4);
            }
        }
        // Fundo do mar
        gc.setFill(light ? Color.web("#134424") : Color.web("#091818"));
        gc.fillRect(0, H - 36, W, 36);
        // Topo escuro
        gc.setFill(light ? Color.web("#082050") : Color.web("#030814"));
        gc.fillRect(0, 0, W, 26);
    }

    void drawTempleBg(GraphicsContext gc) {
        drawGradientBg(gc, "#03000c", "#0c0022", "#160034");
        double t = nano / 1_000_000_000.0;
        // Símbolos cuneiformes decorativos
        gc.setFont(Font.font("Serif", 30));
        gc.setTextAlign(TextAlignment.CENTER);
        String[] runes = { "𒀭", "𒆳", "𒂗", "𒄿", "𒈗", "𒀭", "𒆪", "𒁕" };
        for (int i = 0; i < 8; i++) {
            gc.setFill(Color.rgb(100, 0, 200, 0.12 + Math.sin(t * 0.5 + i) * 0.08));
            gc.fillText(runes[i % runes.length], 100 + i * 165, 85 + (i % 3) * 200);
        }
    }

    /** Quebra texto longo em múltiplas linhas para o Canvas */
    void wrapText(GraphicsContext gc, String text, double x, double y, double maxW, double lineH) {
        gc.setTextAlign(TextAlignment.LEFT);
        String[] words = text.split(" ");
        StringBuilder line = new StringBuilder();
        double ly = y;
        for (String word : words) {
            String test = line.length() > 0 ? line + " " + word : word;
            if (test.length() * 11.0 > maxW) {
                gc.fillText(line.toString(), x, ly);
                line = new StringBuilder(word);
                ly += lineH;
            } else {
                if (line.length() > 0) line.append(" ");
                line.append(word);
            }
        }
        if (line.length() > 0) gc.fillText(line.toString(), x, ly);
    }

    /**
     * Colisão AABB entre dois retângulos.
     * Todos os parâmetros em coordenadas de TELA.
     * (ver ADR-003 e ADR-005)
     */
    boolean rectsHit(double x1, double y1, double w1, double h1,
                     double x2, double y2, double w2, double h2) {
        return x1 < x2 + w2 && x1 + w1 > x2
            && y1 < y2 + h2 && y1 + h1 > y2;
    }

    /** Clamp de valor entre mínimo e máximo */
    double clamp(double v, double min, double max) {
        return Math.max(min, Math.min(max, v));
    }

    /** Spawna explosão de partículas coloridas a partir de um ponto */
    void spawnBurst(double x, double y, Color c) {
        for (int i = 0; i < 14; i++) {
            double angle = Math.random() * Math.PI * 2;
            double speed = 1.5 + Math.random() * 4;
            particles.add(new double[]{
                x, y,
                Math.cos(angle) * speed,
                Math.sin(angle) * speed,
                1.0,              // life (decresce 0.03/frame → ~1s)
                c.getRed(), c.getGreen(), c.getBlue()
            });
        }
    }

    /** Exibe alerta temporário no rodapé por 3.2 segundos */
    void showAlert(String msg) {
        alertMsg  = msg;
        alertTime = nano;
    }

    /**
     * Carrega imagem do classpath Maven (resources/) ou filesystem.
     * Retorna null sem exceção se não encontrar — fallback geométrico cuida do resto.
     */
    Image loadImg(String name) {
        try {
            InputStream is = getClass().getResourceAsStream("/" + name);
            if (is != null) return new Image(is);
            File f = new File("resources/" + name);
            if (f.exists()) return new Image(f.toURI().toString());
            System.out.println("[INFO] " + name + " não encontrado → fallback geométrico");
        } catch (Exception e) {
            System.out.println("[WARN] " + name + ": " + e.getMessage());
        }
        return null;
    }
}
