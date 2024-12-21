import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const Globe = () => {
    const mountRef = useRef(null);

    useEffect(() => {
        if (!mountRef.current) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        mountRef.current.appendChild(renderer.domElement);

        const geometry = new THREE.SphereGeometry(5, 32, 32);
        const texture = new THREE.TextureLoader().load('/earth_texture.jpg'); // Adjust path if necessary
        const material = new THREE.MeshStandardMaterial({ map: texture });
        const earth = new THREE.Mesh(geometry, material);
        scene.add(earth);

        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(5, 5, 5);
        scene.add(light);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableZoom = true;

        camera.position.z = 10;

        // WebSocket for real-time data
        const socket = new WebSocket('ws://your-websocket-url'); // Replace with your WebSocket URL

        socket.onmessage = (event) => {
            const packetData = JSON.parse(event.data);
            const source = new THREE.Vector3(packetData.source.lon, packetData.source.lat, 0);
            const destination = new THREE.Vector3(packetData.destination.lon, packetData.destination.lat, 0);
            drawRoute(source, destination);
            animatePacket(source, destination);
        };

        const drawRoute = (source, destination) => {
            const lineMaterial = new THREE.LineBasicMaterial({ color: 0xff0000 });
            const points = [source, destination];
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, lineMaterial);
            scene.add(line);
        };

        const animatePacket = (source, destination) => {
            const packetGeometry = new THREE.SphereGeometry(0.1, 16, 16);
            const packetMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
            const packet = new THREE.Mesh(packetGeometry, packetMaterial);
            scene.add(packet);

            let startTime;
            const duration = 2000; // 2 seconds
            const animate = (time) => {
                if (!startTime) startTime = time;
                const elapsed = time - startTime;
                const t = Math.min(elapsed / duration, 1);
                packet.position.lerpVectors(source, destination, t);

                if (t < 1) {
                    requestAnimationFrame(animate);
                } else {
                    scene.remove(packet);
                }
            };
            requestAnimationFrame(animate);
        };

        const animate = () => {
            requestAnimationFrame(animate);
            earth.rotation.y += 0.01; // Rotate the Earth
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        // Cleanup
        return () => {
            if (mountRef.current) {
                mountRef.current.removeChild(renderer.domElement);
            }
            socket.close();
            renderer.dispose();
        };
    }, []);

    return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />;
};

export default Globe;
