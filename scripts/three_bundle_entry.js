// L'ingresso del pacchetto three.js della scena 3D della narrativa
// (scripts/build_three_bundle.sh): solo quello che la scena usa.
import { Box3, Color, DirectionalLight, EdgesGeometry, HemisphereLight, LineBasicMaterial,
         LineSegments, PerspectiveCamera, Raycaster, Scene, SRGBColorSpace, Vector2, Vector3,
         WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

window.PYA_THREE = { Box3, Color, DirectionalLight, EdgesGeometry, HemisphereLight,
  LineBasicMaterial, LineSegments, PerspectiveCamera, Raycaster, Scene, SRGBColorSpace,
  Vector2, Vector3, WebGLRenderer, GLTFLoader, OrbitControls };
