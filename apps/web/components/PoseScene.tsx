"use client";
import {Canvas} from "@react-three/fiber";
import {Grid,OrbitControls,Text} from "@react-three/drei";
import * as THREE from "three";
type Landmark={name:string;x:number;y:number;z:number;confidence:number};
type Frame={landmarks:Record<string,Landmark>};
const edges=[["left_shoulder","right_shoulder"],["left_shoulder","left_elbow"],["left_elbow","left_wrist"],["right_shoulder","right_elbow"],["right_elbow","right_wrist"],["left_shoulder","left_hip"],["right_shoulder","right_hip"],["left_hip","right_hip"],["left_hip","left_knee"],["left_knee","left_ankle"],["right_hip","right_knee"],["right_knee","right_ankle"]];
function P({p}:{p:Landmark}){return <mesh position={[(p.x-.5)*4,(.5-p.y)*4,p.z*2]}><sphereGeometry args={[.045,20,20]}/><meshStandardMaterial color={p.name.startsWith("left")?"#42e8ff":"#ffb648"}/></mesh>}
function Bone({a,b}:{a:Landmark;b:Landmark}){const pa=new THREE.Vector3((a.x-.5)*4,(.5-a.y)*4,a.z*2),pb=new THREE.Vector3((b.x-.5)*4,(.5-b.y)*4,b.z*2);const mid=pa.clone().add(pb).multiplyScalar(.5),len=pa.distanceTo(pb);const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),pb.clone().sub(pa).normalize());return <mesh position={mid} quaternion={q}><cylinderGeometry args={[.018,.018,len,10]}/><meshStandardMaterial color="#d9f9ff"/></mesh>}
export function PoseScene({frame}:{frame?:Frame}){return <Canvas camera={{position:[0,0.2,5],fov:42}}><ambientLight intensity={1.7}/><directionalLight position={[4,5,6]} intensity={2}/><Grid args={[8,8]} position={[0,-2,0]}/>{frame&&Object.values(frame.landmarks).map(p=><P key={p.name} p={p}/>)}{frame&&edges.map(([a,b])=>frame.landmarks[a]&&frame.landmarks[b]?<Bone key={a+b} a={frame.landmarks[a]} b={frame.landmarks[b]}/>:null)}<OrbitControls makeDefault/></Canvas>}
