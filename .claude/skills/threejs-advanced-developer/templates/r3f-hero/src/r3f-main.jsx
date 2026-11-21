import { createRoot } from 'react-dom/client';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { ContactShadows, Float, OrbitControls } from '@react-three/drei';
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { buildRoomEnvironment } from './offline-env.js';

// Ambiente sem rede: aplicado à cena e liberado no unmount.
function RoomEnv() {
  const { gl, scene } = useThree();
  useEffect(() => {
    const tex = buildRoomEnvironment(gl);
    scene.environment = tex;
    return () => { scene.environment = null; tex.dispose(); };
  }, [gl, scene]);
  return null;
}

function Hero() {
  const mesh = useRef();
  // Atualiza transformação dentro do loop, sem setState: evita re-render do React a 60fps.
  useFrame((_, dt) => {
    if (mesh.current) mesh.current.rotation.y += dt * 0.15;
  });
  return (
    <Float speed={1.4} rotationIntensity={0.4} floatIntensity={0.6}>
      <mesh ref={mesh} castShadow>
        <torusKnotGeometry args={[1.1, 0.38, 240, 36]} />
        <meshPhysicalMaterial color="#c9d6ff" roughness={0.12} metalness={0}
          transmission={0.92} thickness={1.4} ior={1.45} clearcoat={1} clearcoatRoughness={0.05} />
      </mesh>
    </Float>
  );
}

function App() {
  return (
    <Canvas
      shadows={{ type: THREE.PCFShadowMap }}
      dpr={[1, 2]}
      camera={{ position: [0, 1.4, 9], fov: 38 }}
      gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05, shadowMap: { type: THREE.PCFShadowMap } }}
      style={{ background: '#07080b' }}
    >
      <color attach="background" args={['#07080b']} />
      <fog attach="fog" args={['#07080b', 9, 26]} />
      <directionalLight position={[4, 7, 5]} intensity={2.2} color="#ffe7c4" castShadow />
      <RoomEnv />
      <Hero />
      <ContactShadows position={[0, -1.6, 0]} opacity={0.5} scale={14} blur={2.4} far={4} />
      <OrbitControls enablePan={false} enableDamping dampingFactor={0.06} minDistance={5} maxDistance={14} target={[0, 0.2, 0]} />
    </Canvas>
  );
}

createRoot(document.getElementById('root')).render(<App />);
