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

class GTE_IMPEXP Fluid2InitializeState
{
public:
    // Construction and destruction.  The initial velocity is zero and the
    // initial density is randomly generated with values in [0,1].
    ~Fluid2InitializeState();
    Fluid2InitializeState(int xSize, int ySize, int numXThreads,
        int numYThreads);

    // Member access.  The texels are (velocity.x, velocity.y, 0, density).
    // The third component is unused in the simulation (a 3D simulation will
    // store velocity.z in this component).
    std::shared_ptr<gte::Texture2> const& GetStateTm1() const;
    std::shared_ptr<gte::Texture2> const& GetStateT() const;

    // Compute the initial density and initial velocity for the fluid
    // simulation.
    void Execute(gte::DX11Engine* engine);

private:
    int mNumXGroups, mNumYGroups;
    std::shared_ptr<gte::ComputeShader> mInitializeState;
    std::shared_ptr<gte::Texture2> mDensity;
    std::shared_ptr<gte::Texture2> mVelocity;
    std::shared_ptr<gte::Texture2> mStateTm1;
    std::shared_ptr<gte::Texture2> mStateT;

    static std::string const msHLSLInitializeStateString;
};

}
