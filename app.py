import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Iron Snout - Piggy Arcade Game",
    page_icon="🐷",
    layout="centered",
)

st.title("🐷 Iron Snout - Chú Heo Đấu Sói")
st.caption("Game Arcade đối kháng trên Streamlit & HTML5 Canvas!")

# HTML/CSS/JS Iron Snout Engine
game_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        margin: 0;
        padding: 0;
        background: #111;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        user-select: none;
    }
    #game-container {
        position: relative;
        width: 100%;
        max-width: 650px;
        margin-top: 10px;
    }
    canvas {
        background: #222;
        border: 4px solid #444;
        border-radius: 12px;
        width: 100%;
        height: auto;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .controls {
        margin-top: 15px;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        width: 100%;
        max-width: 400px;
    }
    .btn {
        background: #ff4b4b;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        text-align: center;
        box-shadow: 0 4px 0 #b32d2d;
    }
    .btn:active {
        transform: translateY(2px);
        box-shadow: 0 2px 0 #b32d2d;
    }
    .instructions {
        margin-top: 15px;
        font-size: 14px;
        color: #aaa;
        text-align: center;
    }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas" width="650" height="400"></canvas>
</div>

<div class="controls">
    <div></div>
    <button class="btn" id="btn-up">⬆️ Nhảy</button>
    <div></div>
    <button class="btn" id="btn-left">⬅️ Đấm Trái</button>
    <button class="btn" id="btn-down">⬇️ Cúi</button>
    <button class="btn" id="btn-right">Đấm Phải ➡️</button>
</div>

<div class="instructions">
    <p>🎮 <b>Phím điều khiển (Bàn phím):</b> Phím mũi tên (hoặc WASD)</p>
    <p>⚡ Né đạn/rìu bằng cách <b>Cúi</b> hoặc <b>Nhảy</b>. Phản đòn khi đánh đúng lúc!</p>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let score = 0;
let highScore = localStorage.getItem('iron_snout_highscore') || 0;
let gameOver = false;

// Audio Synth
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSound(freq, type, duration) {
    try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
    } catch(e) {}
}

// Player
const pig = {
    x: 325, y: 300,
    baseY: 300,
    vx: 0, vy: 0,
    state: 'idle', // idle, punch_l, punch_r, duck, jump
    health: 100,
    facing: 'right',
    timer: 0
};

// Enemies & Projectiles
let wolves = [];
let projectiles = [];
let particles = [];

function spawnWolf() {
    if (gameOver) return;
    const side = Math.random() < 0.5 ? 'left' : 'right';
    wolves.push({
        x: side === 'left' ? -40 : 690,
        y: 300,
        type: Math.random() < 0.3 ? 'armed' : 'normal',
        side: side,
        speed: 1.5 + Math.random() * 1.2,
        state: 'walk',
        attackTimer: 0
    });
}

setInterval(spawnWolf, 2000);

// Input Handling
function handleInput(action) {
    if (gameOver) {
        restartGame();
        return;
    }
    
    pig.timer = 12;
    if (action === 'up' && pig.y === pig.baseY) {
        pig.vy = -12;
        pig.state = 'jump';
        playSound(400, 'square', 0.1);
    } else if (action === 'down') {
        pig.state = 'duck';
        playSound(200, 'triangle', 0.1);
    } else if (action === 'left') {
        pig.state = 'punch_l';
        pig.facing = 'left';
        checkHit('left');
        playSound(300, 'sawtooth', 0.08);
    } else if (action === 'right') {
        pig.state = 'punch_r';
        pig.facing = 'right';
        checkHit('right');
        playSound(300, 'sawtooth', 0.08);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowUp' || e.key === 'w') handleInput('up');
    if (e.key === 'ArrowDown' || e.key === 's') handleInput('down');
    if (e.key === 'ArrowLeft' || e.key === 'a') handleInput('left');
    if (e.key === 'ArrowRight' || e.key === 'd') handleInput('right');
});

document.getElementById('btn-up').onclick = () => handleInput('up');
document.getElementById('btn-down').onclick = () => handleInput('down');
document.getElementById('btn-left').onclick = () => handleInput('left');
document.getElementById('btn-right').onclick = () => handleInput('right');

function checkHit(side) {
    const reach = 80;
    // Hit Wolves
    wolves.forEach((w, index) => {
        const dist = Math.abs(w.x - pig.x);
        if (dist < reach && ((side === 'left' && w.x < pig.x) || (side === 'right' && w.x > pig.x))) {
            createParticles(w.x, w.y - 30, '#ff3333');
            if (w.type === 'armed') {
                // Throw weapon
                projectiles.push({
                    x: w.x, y: w.y - 30,
                    vx: side === 'left' ? 8 : -8,
                    vy: -3,
                    reflected: true
                });
            }
            wolves.splice(index, 1);
            score += 10;
            playSound(150, 'sawtooth', 0.15);
        }
    });

    // Reflect Projectiles
    projectiles.forEach((p) => {
        const dist = Math.abs(p.x - pig.x);
        if (dist < reach && !p.reflected) {
            p.vx *= -1.5;
            p.reflected = true;
            score += 15;
            createParticles(p.x, p.y, '#ffff33');
            playSound(600, 'sine', 0.1);
        }
    });
}

function createParticles(x, y, color) {
    for (let i = 0; i < 8; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 6,
            vy: (Math.random() - 0.5) * 6,
            life: 15,
            color: color
        });
    }
}

function restartGame() {
    score = 0;
    pig.health = 100;
    wolves = [];
    projectiles = [];
    gameOver = false;
}

function update() {
    if (gameOver) return;

    // Pig Physics
    pig.y += pig.vy;
    if (pig.y < pig.baseY) {
        pig.vy += 0.8; // Gravity
    } else {
        pig.y = pig.baseY;
        pig.vy = 0;
    }

    if (pig.timer > 0) {
        pig.timer--;
    } else {
        pig.state = 'idle';
    }

    // Wolves Logic
    wolves.forEach((w, index) => {
        if (w.side === 'left') w.x += w.speed;
        else w.x -= w.speed;

        // Wolf throws weapon
        if (w.type === 'armed' && Math.abs(w.x - pig.x) < 220 && Math.random() < 0.02) {
            projectiles.push({
                x: w.x, y: w.y - 25,
                vx: w.side === 'left' ? 4 : -4,
                vy: 0,
                reflected: false
            });
            w.type = 'normal';
        }

        // Hit Pig
        if (Math.abs(w.x - pig.x) < 30 && Math.abs(w.y - pig.y) < 20) {
            pig.health -= 10;
            createParticles(pig.x, pig.y - 20, '#ff0000');
            wolves.splice(index, 1);
            playSound(100, 'square', 0.2);
            if (pig.health <= 0) {
                gameOver = true;
                if (score > highScore) {
                    highScore = score;
                    localStorage.setItem('iron_snout_highscore', highScore);
                }
            }
        }
    });

    // Projectiles Logic
    projectiles.forEach((p, index) => {
        p.x += p.vx;
        p.y += p.vy;

        // Check Hit Pig
        if (!p.reflected && Math.abs(p.x - pig.x) < 25 && Math.abs(p.y - (pig.y - (pig.state === 'duck' ? 0 : 30))) < 20) {
            pig.health -= 15;
            projectiles.splice(index, 1);
            playSound(80, 'square', 0.25);
            if (pig.health <= 0) gameOver = true;
        }

        // Check Reflected Hit Wolves
        if (p.reflected) {
            wolves.forEach((w, wIndex) => {
                if (Math.abs(p.x - w.x) < 30) {
                    wolves.splice(wIndex, 1);
                    projectiles.splice(index, 1);
                    score += 20;
                }
            });
        }
    });

    // Particles
    particles.forEach((pt, index) => {
        pt.x += pt.vx;
        pt.y += pt.vy;
        pt.life--;
        if (pt.life <= 0) particles.splice(index, 1);
    });
}

function draw() {
    // Clear Canvas
    ctx.fillStyle = '#1c1c24';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Ground
    ctx.fillStyle = '#2d2d3a';
    ctx.fillRect(0, 340, canvas.width, 60);
    ctx.fillStyle = '#4fad5b';
    ctx.fillRect(0, 335, canvas.width, 5);

    // Draw Pig
    ctx.save();
    ctx.translate(pig.x, pig.y);
    
    // Pig Body
    ctx.fillStyle = '#ff80ab';
    let pigH = pig.state === 'duck' ? 25 : 45;
    let pigYOffset = pig.state === 'duck' ? -25 : -45;
    ctx.fillRect(-20, pigYOffset, 40, pigH);

    // Pig Nose
    ctx.fillStyle = '#ff4081';
    let noseX = pig.facing === 'right' ? 10 : -20;
    ctx.fillRect(noseX, pigYOffset + 15, 10, 10);

    // Attack Extensions
    if (pig.state === 'punch_l') {
        ctx.fillStyle = '#ff80ab';
        ctx.fillRect(-45, pigYOffset + 10, 25, 12);
    } else if (pig.state === 'punch_r') {
        ctx.fillStyle = '#ff80ab';
        ctx.fillRect(20, pigYOffset + 10, 25, 12);
    }
    ctx.restore();

    // Draw Wolves
    wolves.forEach(w => {
        ctx.fillStyle = '#78909c';
        ctx.fillRect(w.x - 15, w.y - 40, 30, 40);
        // Eyes
        ctx.fillStyle = '#ff5252';
        ctx.fillRect(w.side === 'left' ? w.x + 2 : w.x - 8, w.y - 35, 6, 6);
        // Weapon
        if (w.type === 'armed') {
            ctx.fillStyle = '#b0bec5';
            ctx.fillRect(w.x + (w.side === 'left' ? 12 : -18), w.y - 30, 6, 18);
        }
    });

    // Draw Projectiles
    projectiles.forEach(p => {
        ctx.fillStyle = p.reflected ? '#ffd700' : '#cfd8dc';
        ctx.beginPath();
        ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
        ctx.fill();
    });

    // Draw Particles
    particles.forEach(pt => {
        ctx.fillStyle = pt.color;
        ctx.fillRect(pt.x, pt.y, 4, 4);
    });

    // HUD
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 18px Arial';
    ctx.fillText(`Máu: ${pig.health}%`, 20, 30);
    ctx.fillText(`Điểm: ${score}`, 20, 55);
    ctx.fillText(`Kỷ Lục: ${highScore}`, 520, 30);

    // Game Over Overlay
    if (gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#ff5252';
        ctx.font = 'bold 36px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER!', canvas.width / 2, 170);
        ctx.fillStyle = '#fff';
        ctx.font = '20px Arial';
        ctx.fillText(`Tổng Điểm: ${score}`, canvas.width / 2, 210);
        ctx.fillText('Bấm nút bất kỳ hoặc nhấp vào đây để chơi lại', canvas.width / 2, 250);
        ctx.textAlign = 'left';
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>
"""

components.html(game_code, height=580)
