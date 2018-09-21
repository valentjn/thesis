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

class GTE_IMPEXP Fluid3InitializeState
{
public:
    // Construction and destruction.  The initial velocity is zero and the
    // initial density is randomly generated with values in [0,1].
    ~Fluid3InitializeState();
    Fluid3InitializeState(int xSize, int ySize, int zSize, int numXThreads,
        int numYThreads, int numZThreads);

    // Member access.  The texels are (velocity.xyz, density).
    std::shared_ptr<gte::Texture3> const& GetStateTm1() const;
    std::shared_ptr<gte::Texture3> const& GetStateT() const;

    // Compute the initial density and initial velocity for the fluid
    // simulation.
    void Execute(gte::DX11Engine* engine);

private:
    int mNumXGroups, mNumYGroups, mNumZGroups;
    std::shared_ptr<gte::ComputeShader> mInitializeState;
    std::shared_ptr<gte::Texture3> mDensity;
    std::shared_ptr<gte::Texture3> mVelocity;
    std::shared_ptr<gte::Texture3> mStateTm1;
    std::shared_ptr<gte::Texture3> mStateT;

    static std::string const msHLSLInitializeStateString;
};

}
