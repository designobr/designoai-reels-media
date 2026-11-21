import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// Ambiente HDR gerado em código: funciona offline e sem carregar .hdr externo.
// Use no lugar de <Environment preset="..."/> quando a rede for restrita.
export function buildRoomEnvironment(renderer) {
  const pmrem = new THREE.PMREMGenerator(renderer);
  const texture = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  pmrem.dispose();
  return texture;
}
