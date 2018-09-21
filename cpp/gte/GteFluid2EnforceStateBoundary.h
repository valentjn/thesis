// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteTexture2.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Fluid2EnforceStateBoundary
{
public:
    // Construction and destruction.  Clamp the velocity vectors at the image
    // boundary to ensure they do not point outside the domain.  For example,
    // let image(x,y) have velocity (vx,vy).  At the boundary pixel (x,0),
    // the velocity is clamped to (vx,0).  At the boundary pixel (0,y), the
    // velocity is clamped to (0,vy).  The density is set to zero on the image
    // boundary.
    ~Fluid2EnforceStateBoundary();
    Fluid2EnforceStateBoundary(int xSize, int ySize, int numXThreads,
        int numYThreads);

    // Set the density and velocity values at the image boundary as described
    // in the comments for the constructor.  The state texture has texels
    // (velocity.x, velocity.y, 0, density).
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture2> const& state);

private:
    int mNumXGroups, mNumYGroups;
    std::shared_ptr<gte::ComputeShader> mCopyXEdge;
    std::shared_ptr<gte::ComputeShader> mWriteXEdge;
    std::shared_ptr<gte::ComputeShader> mCopyYEdge;
    std::shared_ptr<gte::ComputeShader> mWriteYEdge;
    std::shared_ptr<gte::Texture1> mXMin;
    std::shared_ptr<gte::Texture1> mXMax;
    std::shared_ptr<gte::Texture1> mYMin;
    std::shared_ptr<gte::Texture1> mYMax;

    static std::string const msHLSLEnforceStateBoundaryString;
};

}
