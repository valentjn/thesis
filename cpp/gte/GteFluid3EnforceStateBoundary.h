// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteTexture3.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Fluid3EnforceStateBoundary
{
public:
    // Construction and destruction.  Clamp the velocity vectors at the image
    // boundary to ensure they do not point outside the domain.  For example,
    // let image(x,y,z) have velocity (vx,vy,vz).  At the boundary pixel
    // (x,y,0), the velocity is clamped to (vx,vy,0).  The density is set to
    // zero on the image boundary.
    ~Fluid3EnforceStateBoundary();
    Fluid3EnforceStateBoundary(int xSize, int ySize, int zSize,
        int numXThreads, int numYThreads, int numZThreads);

    // Set the density and velocity values at the image boundary as described
    // in the comments for the constructor.  The state texture has texels
    // (velocity.x, velocity.y, velocity.z, density).
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture3> const& state);

private:
    int mNumXGroups, mNumYGroups, mNumZGroups;
    std::shared_ptr<gte::ComputeShader> mCopyXFace;
    std::shared_ptr<gte::ComputeShader> mWriteXFace;
    std::shared_ptr<gte::ComputeShader> mCopyYFace;
    std::shared_ptr<gte::ComputeShader> mWriteYFace;
    std::shared_ptr<gte::ComputeShader> mCopyZFace;
    std::shared_ptr<gte::ComputeShader> mWriteZFace;
    std::shared_ptr<gte::Texture2> mXMin;
    std::shared_ptr<gte::Texture2> mXMax;
    std::shared_ptr<gte::Texture2> mYMin;
    std::shared_ptr<gte::Texture2> mYMax;
    std::shared_ptr<gte::Texture2> mZMin;
    std::shared_ptr<gte::Texture2> mZMax;

    static std::string const msHLSLEnforceStateBoundaryString;
};

}
