// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.41 (2015/05/31)

#pragma once

#if defined(WIN32)

// Applications
#include <gte/GteCommand.h>
#include <gte/GteEnvironment.h>
#include <gte/GteWICFileIO.h>
#include <gte/GteWindow.h>
#include <gte/GteWindowSystem.h>

// Graphics/Effects
#include <gte/GteConstantColorEffect.h>
#include <gte/GteFont.h>
#include <gte/GteFontArialW400H18.h>
#include <gte/GteLightingConstants.h>
#include <gte/GteLightingEffect.h>
#include <gte/GteLightAmbientEffect.h>
#include <gte/GteLightDirectionPerPixelEffect.h>
#include <gte/GteLightDirectionPerVertexEffect.h>
#include <gte/GteLightPointPerPixelEffect.h>
#include <gte/GteLightPointPerVertexEffect.h>
#include <gte/GteLightSpotPerPixelEffect.h>
#include <gte/GteLightSpotPerVertexEffect.h>
#include <gte/GteOverlayEffect.h>
#include <gte/GteTextEffect.h>
#include <gte/GteTexture2Effect.h>
#include <gte/GteTexture3Effect.h>
#include <gte/GteVertexColorEffect.h>
#include <gte/GteVisualEffect.h>

// Graphics/Resources
#include <gte/GteDataFormat.h>
#include <gte/GteGraphicsObject.h>
#include <gte/GteResource.h>

// Graphics/Resources/Buffers
#include <gte/GteBuffer.h>
#include <gte/GteConstantBuffer.h>
#include <gte/GteIndexBuffer.h>
#include <gte/GteIndexFormat.h>
#include <gte/GteIndirectArgumentsBuffer.h>
#include <gte/GteMemberLayout.h>
#include <gte/GteRawBuffer.h>
#include <gte/GteStructuredBuffer.h>
#include <gte/GteTextureBuffer.h>
#include <gte/GteTypedBuffer.h>
#include <gte/GteVertexBuffer.h>
#include <gte/GteVertexFormat.h>

// Graphics/Resources/State
#include <gte/GteBlendState.h>
#include <gte/GteDepthStencilState.h>
#include <gte/GteDrawingState.h>
#include <gte/GteRasterizerState.h>
#include <gte/GteSamplerState.h>

// Graphics/Resources/Textures
#include <gte/GteDrawTarget.h>
#include <gte/GteTexture.h>
#include <gte/GteTexture1.h>
#include <gte/GteTexture1Array.h>
#include <gte/GteTexture2.h>
#include <gte/GteTexture2Array.h>
#include <gte/GteTexture3.h>
#include <gte/GteTextureArray.h>
#include <gte/GteTextureCube.h>
#include <gte/GteTextureCubeArray.h>
#include <gte/GteTextureDS.h>
#include <gte/GteTextureRT.h>
#include <gte/GteTextureSingle.h>

// Graphics/SceneGraph
#include <gte/GteBoundingSphere.h>
#include <gte/GteCamera.h>
#include <gte/GteCuller.h>
#include <gte/GteCullingPlane.h>
#include <gte/GteMeshFactory.h>
#include <gte/GteNode.h>
#include <gte/GtePicker.h>
#include <gte/GtePickRecord.h>
#include <gte/GteSpatial.h>
#include <gte/GteVisibleSet.h>
#include <gte/GteVisual.h>

// Graphics/Shaders
#include <gte/GteComputeShader.h>
#include <gte/GteGeometryShader.h>
#include <gte/GtePixelShader.h>
#include <gte/GteShader.h>
#include <gte/GteShaderFactory.h>
#include <gte/GteVertexShader.h>

// Graphics/DirectX11/DX11
#include <gte/GteDX11Engine.h>
#include <gte/GteDX11GraphicsObject.h>
#include <gte/GteDX11Include.h>
#include <gte/GteDX11PerformanceCounter.h>

// Graphics/DirectX11/DX11/InputLayout
#include <gte/GteDX11InputLayout.h>
#include <gte/GteDX11InputLayoutManager.h>

// Graphics/DirectX11/DX11/Resources
#include <gte/GteDX11Resource.h>

// Graphics/DirectX11/DX11/Resources/Buffers
#include <gte/GteDX11Buffer.h>
#include <gte/GteDX11ConstantBuffer.h>
#include <gte/GteDX11IndexBuffer.h>
#include <gte/GteDX11IndirectArgumentsBuffer.h>
#include <gte/GteDX11RawBuffer.h>
#include <gte/GteDX11StructuredBuffer.h>
#include <gte/GteDX11TextureBuffer.h>
#include <gte/GteDX11VertexBuffer.h>

// Graphics/DirectX11/DX11/Resources/Textures
#include <gte/GteDX11DrawTarget.h>
#include <gte/GteDX11Texture.h>
#include <gte/GteDX11Texture1.h>
#include <gte/GteDX11Texture1Array.h>
#include <gte/GteDX11Texture2.h>
#include <gte/GteDX11Texture2Array.h>
#include <gte/GteDX11Texture3.h>
#include <gte/GteDX11TextureArray.h>
#include <gte/GteDX11TextureCube.h>
#include <gte/GteDX11TextureCubeArray.h>
#include <gte/GteDX11TextureDS.h>
#include <gte/GteDX11TextureRT.h>
#include <gte/GteDX11TextureSingle.h>

// Graphics/DirectX11/DX11/Shaders
#include <gte/GteDX11ComputeShader.h>
#include <gte/GteDX11GeometryShader.h>
#include <gte/GteDX11PixelShader.h>
#include <gte/GteDX11Shader.h>
#include <gte/GteDX11VertexShader.h>

// Graphics/DirectX11/DX11/State
#include <gte/GteDX11BlendState.h>
#include <gte/GteDX11DepthStencilState.h>
#include <gte/GteDX11DrawingState.h>
#include <gte/GteDX11RasterizerState.h>
#include <gte/GteDX11SamplerState.h>

// Graphics/DirectX11/DXGI
#include <gte/GteDXGIAdapter.h>
#include <gte/GteDXGIOutput.h>

// Graphics/DirectX11/HLSL
#include <gte/GteHLSLBaseBuffer.h>
#include <gte/GteHLSLByteAddressBuffer.h>
#include <gte/GteHLSLConstantBuffer.h>
#include <gte/GteHLSLFactory.h>
#include <gte/GteHLSLParameter.h>
#include <gte/GteHLSLResource.h>
#include <gte/GteHLSLResourceBindInfo.h>
#include <gte/GteHLSLSamplerState.h>
#include <gte/GteHLSLShader.h>
#include <gte/GteHLSLShaderFactory.h>
#include <gte/GteHLSLShaderType.h>
#include <gte/GteHLSLShaderVariable.h>
#include <gte/GteHLSLStructuredBuffer.h>
#include <gte/GteHLSLTexture.h>
#include <gte/GteHLSLTextureArray.h>
#include <gte/GteHLSLTextureBuffer.h>

// LowLevel/DataTypes
#include <gte/GteComputeModel.h>

// LowLevel/Logger
#include <gte/GteLogReporter.h>
#include <gte/GteLogToMessageBox.h>
#include <gte/GteLogToOutputWindow.h>

// LowLevel/Timer
#include <gte/GteTimer.h>

// Physics/Fluid2
#include <gte/GteFluid2.h>
#include <gte/GteFluid2AdjustVelocity.h>
#include <gte/GteFluid2ComputeDivergence.h>
#include <gte/GteFluid2EnforceStateBoundary.h>
#include <gte/GteFluid2InitializeSource.h>
#include <gte/GteFluid2InitializeState.h>
#include <gte/GteFluid2Parameters.h>
#include <gte/GteFluid2SolvePoisson.h>
#include <gte/GteFluid2UpdateState.h>

// Physics/Fluid3
#include <gte/GteFluid3.h>
#include <gte/GteFluid3AdjustVelocity.h>
#include <gte/GteFluid3ComputeDivergence.h>
#include <gte/GteFluid3EnforceStateBoundary.h>
#include <gte/GteFluid3InitializeSource.h>
#include <gte/GteFluid3InitializeState.h>
#include <gte/GteFluid3Parameters.h>
#include <gte/GteFluid3SolvePoisson.h>
#include <gte/GteFluid3UpdateState.h>

#endif

// Imagics
#include <gte/GteHistogram.h>
#include <gte/GteImage.h>
#include <gte/GteImage1.h>
#include <gte/GteImage2.h>
#include <gte/GteImage3.h>
#include <gte/GteImageUtility2.h>
#include <gte/GteImageUtility3.h>
#include <gte/GteMarchingCubes.h>
#include <gte/GteMarchingCubesTable.h>
#include <gte/GteSurfaceExtractor.h>

// LowLevel/DataTypes
#include <gte/GteArray2.h>
#include <gte/GteAtomicMinMax.h>
#include <gte/GteMinHeap.h>
#include <gte/GteRangeIteration.h>
#include <gte/GteThreadSafeMap.h>
#include <gte/GteThreadSafeQueue.h>
#include <gte/GteWrapper.h>

// LowLevel/Graphs
#include <gte/GteEdgeKey.h>
#include <gte/GteETManifoldMesh.h>
#include <gte/GteFeatureKey.h>
#include <gte/GteTetrahedronKey.h>
#include <gte/GteTriangleKey.h>
#include <gte/GteTSManifoldMesh.h>
#include <gte/GteVEManifoldMesh.h>
#include <gte/GteUniqueVerticesTriangles.h>

// LowLevel/Logger
#include <gte/GteLogger.h>
#include <gte/GteLogToFile.h>
#include <gte/GteLogToStdout.h>
#include <gte/GteLogToStringArray.h>

// LowLevel/Memory
#include <gte/GteMemory.h>

// Mathematics/Algebra
#include <gte/GteAxisAngle.h>
#include <gte/GteBandedMatrix.h>
#include <gte/GteConvertCoordinates.h>
#include <gte/GteEulerAngles.h>
#include <gte/GteGMatrix.h>
#include <gte/GteGVector.h>
#include <gte/GteMatrix.h>
#include <gte/GteMatrix2x2.h>
#include <gte/GteMatrix3x3.h>
#include <gte/GteMatrix4x4.h>
#include <gte/GtePolynomial1.h>
#include <gte/GteQuaternion.h>
#include <gte/GteRotation.h>
#include <gte/GteTransform.h>
#include <gte/GteVector.h>
#include <gte/GteVector2.h>
#include <gte/GteVector3.h>
#include <gte/GteVector4.h>

// Mathematics/Approximation
#include <gte/GteApprCircle2.h>
#include <gte/GteApprEllipse2.h>
#include <gte/GteApprEllipsoid3.h>
#include <gte/GteApprGaussian2.h>
#include <gte/GteApprGaussian3.h>
#include <gte/GteApprGreatCircle3.h>
#include <gte/GteApprHeightLine2.h>
#include <gte/GteApprHeightPlane3.h>
#include <gte/GteApprOrthogonalLine2.h>
#include <gte/GteApprOrthogonalLine3.h>
#include <gte/GteApprOrthogonalPlane3.h>
#include <gte/GteApprParaboloid3.h>
#include <gte/GteApprPolynomial2.h>
#include <gte/GteApprPolynomial3.h>
#include <gte/GteApprPolynomial4.h>
#include <gte/GteApprPolynomialSpecial2.h>
#include <gte/GteApprPolynomialSpecial3.h>
#include <gte/GteApprPolynomialSpecial4.h>
#include <gte/GteApprQuadratic2.h>
#include <gte/GteApprQuadratic3.h>
#include <gte/GteApprSphere3.h>

// Mathematics/Arithmetic
#include <gte/GteArithmetic.h>
#include <gte/GteBitHacks.h>
#include <gte/GteBSNumber.h>
#include <gte/GteBSPrecision.h>
#include <gte/GteBSRational.h>
#include <gte/GteIEEEBinary.h>
#include <gte/GteIEEEBinary16.h>
#include <gte/GteUIntegerALU32.h>
#include <gte/GteUIntegerAP32.h>
#include <gte/GteUIntegerFP32.h>

// Mathematics/ComputationalGeometry
#include <gte/GteConstrainedDelaunay2.h>
#include <gte/GteConvexHull2.h>
#include <gte/GteConvexHull3.h>
#include <gte/GteDelaunay2.h>
#include <gte/GteDelaunay2Mesh.h>
#include <gte/GteDelaunay3.h>
#include <gte/GteDelaunay3Mesh.h>
#include <gte/GteGenerateMeshUV.h>
#include <gte/GteMinimumAreaBox2.h>
#include <gte/GteMinimumAreaCircle2.h>
#include <gte/GteMinimumVolumeBox3.h>
#include <gte/GteMinimumVolumeSphere3.h>
#include <gte/GteNearestNeighborQuery.h>
#include <gte/GtePlanarMesh.h>
#include <gte/GtePrimalQuery2.h>
#include <gte/GtePrimalQuery3.h>
#include <gte/GteSeparatePoints2.h>
#include <gte/GteSeparatePoints3.h>
#include <gte/GteTriangulateCDT.h>
#include <gte/GteTriangulateEC.h>

// Mathematics/Containment
#include <gte/GteContCapsule3.h>
#include <gte/GteContCircle2.h>
#include <gte/GteContCylinder3.h>
#include <gte/GteContEllipse2.h>
#include <gte/GteContEllipse2MinCR.h>
#include <gte/GteContEllipsoid3.h>
#include <gte/GteContEllipsoid3MinCR.h>
#include <gte/GteContOrientedBox2.h>
#include <gte/GteContOrientedBox3.h>
#include <gte/GteContPointInPolygon2.h>
#include <gte/GteContPointInPolyhedron3.h>
#include <gte/GteContScribeCircle2.h>
#include <gte/GteContScribeCircle3Sphere3.h>
#include <gte/GteContSphere3.h>

// Mathematics/CurvesSurfacesVolumes
#include <gte/GteBasisFunction.h>
#include <gte/GteBezierCurve.h>
#include <gte/GteBSplineCurve.h>
#include <gte/GteBSplineCurveFit.h>
#include <gte/GteBSplineSurface.h>
#include <gte/GteBSplineSurfaceFit.h>
#include <gte/GteBSplineVolume.h>
#include <gte/GteDarbouxFrame.h>
#include <gte/GteFrenetFrame.h>
#include <gte/GteNaturalSplineCurve.h>
#include <gte/GteNURBSCurve.h>
#include <gte/GteNURBSSurface.h>
#include <gte/GteNURBSVolume.h>
#include <gte/GteParametricCurve.h>
#include <gte/GteParametricSurface.h>
#include <gte/GteRectangleSurface.h>
#include <gte/GteTCBSplineCurve.h>
#include <gte/GteTubeSurface.h>

// Mathematics/Distance
#include <gte/GteDCPQuery.h>

// Mathematics/Distance/3D
#include <gte/GteDistPoint3Circle3.h>
#include <gte/GteDistPoint3Cylinder3.h>
#include <gte/GteDistPoint3Frustum3.h>
#include <gte/GteDistPoint3Plane3.h>
#include <gte/GteDistPoint3Rectangle3.h>
#include <gte/GteDistPoint3Tetrahedron3.h>

#include <gte/GteDistLine3Circle3.h>
#include <gte/GteDistLine3Rectangle3.h>
#include <gte/GteDistLine3Triangle3.h>
#include <gte/GteDistRay3Rectangle3.h>
#include <gte/GteDistRay3Triangle3.h>
#include <gte/GteDistSegment3Rectangle3.h>
#include <gte/GteDistSegment3Triangle3.h>

#include <gte/GteDistLine3AlignedBox3.h>
#include <gte/GteDistLine3OrientedBox3.h>
#include <gte/GteDistRay3AlignedBox3.h>
#include <gte/GteDistRay3OrientedBox3.h>
#include <gte/GteDistSegment3AlignedBox3.h>
#include <gte/GteDistSegment3OrientedBox3.h>

#include <gte/GteDistCircle3Circle3.h>
#include <gte/GteDistRectangle3Rectangle3.h>
#include <gte/GteDistTriangle3Rectangle3.h>
#include <gte/GteDistTriangle3Triangle3.h>

// Mathematics/Distance/ND
#include <gte/GteDistLineLine.h>
#include <gte/GteDistLineRay.h>
#include <gte/GteDistLineSegment.h>
#include <gte/GteDistPointAlignedBox.h>
#include <gte/GteDistPointHyperellipsoid.h>
#include <gte/GteDistPointLine.h>
#include <gte/GteDistPointOrientedBox.h>
#include <gte/GteDistPointRay.h>
#include <gte/GteDistPointSegment.h>
#include <gte/GteDistPointTriangle.h>
#include <gte/GteDistPointTriangleExact.h>
#include <gte/GteDistRayRay.h>
#include <gte/GteDistRaySegment.h>
#include <gte/GteDistSegmentSegment.h>
#include <gte/GteDistSegmentSegmentExact.h>

// Mathematics/Functions
#include <gte/GteACosEstimate.h>
#include <gte/GteASinEstimate.h>
#include <gte/GteATanEstimate.h>
#include <gte/GteChebyshevRatio.h>
#include <gte/GteConstants.h>
#include <gte/GteCosEstimate.h>
#include <gte/GteExp2Estimate.h>
#include <gte/GteExpEstimate.h>
#include <gte/GteFunctions.h>
#include <gte/GteInvSqrtEstimate.h>
#include <gte/GteLog2Estimate.h>
#include <gte/GteLogEstimate.h>
#include <gte/GteSinEstimate.h>
#include <gte/GteSlerpEstimate.h>
#include <gte/GteSqrtEstimate.h>
#include <gte/GteTanEstimate.h>

// Mathematics/GeometricPrimitives/2D
#include <gte/GteArc2.h>
#include <gte/GtePolygon2.h>

// Mathematics/GeometricPrimitives/3D
#include <gte/GteCircle3.h>
#include <gte/GteCylinder3.h>
#include <gte/GteEllipse3.h>
#include <gte/GteFrustum3.h>
#include <gte/GtePolyhedron3.h>
#include <gte/GteTetrahedron3.h>
#include <gte/GteTorus3.h>

// Mathematics/GeometricPrimitives/ND
#include <gte/GteAlignedBox.h>
#include <gte/GteCapsule.h>
#include <gte/GteCone.h>
#include <gte/GteHalfspace.h>
#include <gte/GteHyperellipsoid.h>
#include <gte/GteHyperplane.h>
#include <gte/GteHypersphere.h>
#include <gte/GteLine.h>
#include <gte/GteOrientedBox.h>
#include <gte/GteRay.h>
#include <gte/GteRectangle.h>
#include <gte/GteSegment.h>
#include <gte/GteTriangle.h>

// Mathematics/Interpolation
#include <gte/GteIntpAkima1.h>
#include <gte/GteIntpAkimaUniform1.h>
#include <gte/GteIntpAkimaUniform2.h>
#include <gte/GteIntpAkimaUniform3.h>
#include <gte/GteIntpBicubic2.h>
#include <gte/GteIntpBilinear2.h>
#include <gte/GteIntpLinearNonuniform2.h>
#include <gte/GteIntpLinearNonuniform3.h>
#include <gte/GteIntpQuadraticNonuniform2.h>
#include <gte/GteIntpSphere2.h>
#include <gte/GteIntpThinPlateSpline2.h>
#include <gte/GteIntpThinPlateSpline3.h>
#include <gte/GteIntpTricubic3.h>
#include <gte/GteIntpTrilinear3.h>
#include <gte/GteIntpVectorField2.h>

// Mathematics/Intersection
#include <gte/GteFIQuery.h>
#include <gte/GteTIQuery.h>
#include <gte/GteIntrIntervals.h>

// Mathematics/Intersection/2D
#include <gte/GteIntrLine2Line2.h>
#include <gte/GteIntrLine2Ray2.h>
#include <gte/GteIntrLine2Segment2.h>
#include <gte/GteIntrRay2Ray2.h>
#include <gte/GteIntrRay2Segment2.h>
#include <gte/GteIntrSegment2Segment2.h>

#include <gte/GteIntrArc2Arc2.h>
#include <gte/GteIntrCircle2Arc2.h>
#include <gte/GteIntrCircle2Circle2.h>
#include <gte/GteIntrEllipse2Ellipse2.h>
#include <gte/GteIntrLine2AlignedBox2.h>
#include <gte/GteIntrLine2Arc2.h>
#include <gte/GteIntrLine2Circle2.h>
#include <gte/GteIntrLine2OrientedBox2.h>
#include <gte/GteIntrLine2Triangle2.h>
#include <gte/GteIntrRay2AlignedBox2.h>
#include <gte/GteIntrRay2Arc2.h>
#include <gte/GteIntrRay2Circle2.h>
#include <gte/GteIntrRay2OrientedBox2.h>
#include <gte/GteIntrRay2Triangle2.h>
#include <gte/GteIntrSegment2AlignedBox2.h>
#include <gte/GteIntrSegment2Arc2.h>
#include <gte/GteIntrSegment2Circle2.h>
#include <gte/GteIntrSegment2OrientedBox2.h>
#include <gte/GteIntrSegment2Triangle2.h>

#include <gte/GteIntrAlignedBox2AlignedBox2.h>
#include <gte/GteIntrAlignedBox2OrientedBox2.h>
#include <gte/GteIntrOrientedBox2Circle2.h>
#include <gte/GteIntrOrientedBox2Cone2.h>
#include <gte/GteIntrOrientedBox2OrientedBox2.h>

// Mathematics/Intersection/3D
#include <gte/GteIntrLine3Plane3.h>
#include <gte/GteIntrLine3Triangle3.h>
#include <gte/GteIntrRay3Plane3.h>
#include <gte/GteIntrRay3Triangle3.h>
#include <gte/GteIntrSegment3Plane3.h>
#include <gte/GteIntrSegment3Triangle3.h>

#include <gte/GteIntrHalfspace3Segment3.h>
#include <gte/GteIntrLine3AlignedBox3.h>
#include <gte/GteIntrLine3Capsule3.h>
#include <gte/GteIntrLine3Cone3.h>
#include <gte/GteIntrLine3Cylinder3.h>
#include <gte/GteIntrLine3Ellipsoid3.h>
#include <gte/GteIntrLine3OrientedBox3.h>
#include <gte/GteIntrLine3Sphere3.h>
#include <gte/GteIntrRay3AlignedBox3.h>
#include <gte/GteIntrRay3Capsule3.h>
#include <gte/GteIntrRay3Cone3.h>
#include <gte/GteIntrRay3Cylinder3.h>
#include <gte/GteIntrRay3Ellipsoid3.h>
#include <gte/GteIntrRay3OrientedBox3.h>
#include <gte/GteIntrRay3Sphere3.h>
#include <gte/GteIntrSegment3AlignedBox3.h>
#include <gte/GteIntrSegment3Capsule3.h>
#include <gte/GteIntrSegment3Cone3.h>
#include <gte/GteIntrSegment3Cylinder3.h>
#include <gte/GteIntrSegment3Ellipsoid3.h>
#include <gte/GteIntrSegment3OrientedBox3.h>
#include <gte/GteIntrSegment3Sphere3.h>

#include <gte/GteIntrPlane3Circle3.h>
#include <gte/GteIntrPlane3Plane3.h>
#include <gte/GteIntrPlane3Triangle3.h>

#include <gte/GteIntrHalfspace3Triangle3.h>
#include <gte/GteIntrPlane3Capsule3.h>
#include <gte/GteIntrPlane3Cylinder3.h>
#include <gte/GteIntrPlane3Ellipsoid3.h>
#include <gte/GteIntrPlane3OrientedBox3.h>
#include <gte/GteIntrPlane3Sphere3.h>

#include <gte/GteIntrAlignedBox3AlignedBox3.h>
#include <gte/GteIntrAlignedBox3OrientedBox3.h>
#include <gte/GteIntrCapsule3Capsule3.h>
#include <gte/GteIntrEllipsoid3Ellipsoid3.h>
#include <gte/GteIntrHalfspace3Capsule3.h>
#include <gte/GteIntrHalfspace3Cylinder3.h>
#include <gte/GteIntrHalfspace3Ellipsoid3.h>
#include <gte/GteIntrHalfspace3OrientedBox3.h>
#include <gte/GteIntrHalfspace3Sphere3.h>
#include <gte/GteIntrOrientedBox3Cone3.h>
#include <gte/GteIntrOrientedBox3Frustum3.h>
#include <gte/GteIntrOrientedBox3OrientedBox3.h>
#include <gte/GteIntrOrientedBox3Sphere3.h>
#include <gte/GteIntrSphere3Cone3.h>
#include <gte/GteIntrSphere3Frustum3.h>
#include <gte/GteIntrSphere3Sphere3.h>

// Mathematics/NumericalMethods
#include <gte/GteGaussianElimination.h>
#include <gte/GteIntegration.h>
#include <gte/GteLinearSystem.h>
#include <gte/GteMinimize1.h>
#include <gte/GteMinimizeN.h>
#include <gte/GteOdeEuler.h>
#include <gte/GteOdeImplicitEuler.h>
#include <gte/GteOdeMidpoint.h>
#include <gte/GteOdeRungeKutta4.h>
#include <gte/GteOdeSolver.h>
#include <gte/GteRootsBisection.h>
#include <gte/GteRootsBrentsMethod.h>
#include <gte/GteRootsPolynomial.h>
#include <gte/GteSingularValueDecomposition.h>
#include <gte/GteSymmetricEigensolver.h>
#include <gte/GteSymmetricEigensolver2x2.h>
#include <gte/GteSymmetricEigensolver3x3.h>

// Mathematics/Projection
#include <gte/GteProjection.h>

// Physics/RigidBody
#include <gte/GteMassSpringArbitrary.h>
#include <gte/GteMassSpringCurve.h>
#include <gte/GteMassSpringSurface.h>
#include <gte/GteMassSpringVolume.h>
#include <gte/GteParticleSystem.h>
#include <gte/GtePolyhedralMassProperties.h>
#include <gte/GteRigidBody.h>
