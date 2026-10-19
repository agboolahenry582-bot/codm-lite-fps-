from flask import Flask, render_template_string
from flask_socketio import SocketIO
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'codm_ultimate_secret_key_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

PLAYERS = {}
LEADERBOARD = {}

# Paste your full HTML_TEMPLATE here - use the one you sent, but with this fix at bottom:

HTML_TEMPLATE = """ ... your full HTML from above ... 

        function setupMobileControls() {
            const zone = document.getElementById('joystick-zone');
            const knob = document.getElementById('joystick-knob');
            const fireBtn = document.getElementById('mobile-fire');
            let startX=0,startY=0,moveX=0,moveY=0,active=false;
            zone.addEventListener('touchstart',(e)=>{
                active=true;
                let t=e.touches[0];
                startX=t.clientX; startY=t.clientY;
            });
            zone.addEventListener('touchmove',(e)=>{
                if(!active) return;
                let t=e.touches[0];
                let dx=t.clientX-startX, dy=t.clientY-startY;
                let dist=Math.sqrt(dx*dx+dy*dy);
                if(dist>45){ dx=dx/dist*45; dy=dy/dist*45; }
                knob.style.transform=`translate(${dx}px, ${dy}px)`;
                moveX=dx/45; moveY=dy/45;
                if(gameState==='PARACHUTE'){
                    playerMesh.position.x+=moveX*0.5;
                    playerMesh.position.z+=moveY*0.5;
                } else if(gameState==='GROUND'){
                    playerMesh.position.x+=moveX*0.6;
                    playerMesh.position.z+=moveY*0.6;
                }
                e.preventDefault();
            },{passive:false});
            zone.addEventListener('touchend',()=>{
                active=false; knob.style.transform='translate(0,0)'; moveX=0; moveY=0;
            });
            fireBtn.addEventListener('touchstart',(e)=>{ e.preventDefault(); shoot(); });
        }

        function onWindowResize(){
            camera.aspect=window.innerWidth/window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth,window.innerHeight);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('player_join')
def handle_join(data):
    PLAYERS[request.sid] = {'username': data['username'], 'x':0,'y':150,'z':0,'kills':0}
    socketio.emit('player_joined', {'id': request.sid, **PLAYERS[request.sid]})
    # send existing players
    from flask import request
    socketio.emit('current_players', PLAYERS, to=request.sid)

@socketio.on('player_move')
def handle_move(data):
    if request.sid in PLAYERS:
        PLAYERS[request.sid].update(data)
        socketio.emit('player_moved', {'id': request.sid, **data}, broadcast=True, include_self=False)

@socketio.on('shoot_player')
def handle_shoot(data):
    target = data.get('targetId')
    dmg = data.get('damage', 25)
    if target in PLAYERS:
        socketio.emit('player_shot_event', {'targetId': target, 'damage': dmg, 'shooter': request.sid}, broadcast=True)
        # kill tracking
        if target in PLAYERS:
            # simplistic: if shooter kills, increase
            pass

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in PLAYERS:
        del PLAYERS[request.sid]
    socketio.emit('player_disconnected', request.sid, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
