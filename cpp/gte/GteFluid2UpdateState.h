// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteFluid2Parameters.h>
#include <gte/GteTexture2.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Fluid2UpdateState
{
public:
    // Construction and destruction.
    ~Fluid2UpdateState();
    Fluid2UpdateState(int xSize, int ySize, int numXThreads, int numYThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Member access.  The texels are (velocity.x, velocity.y, 0, density).
    // The third component is unused in the simulation (a 3D simulation will
    // store velocity.z in this component).
    std::shared_ptr<gte::Texture2> const& GetUpdateState() const;

    // Update the state for the fluid simulation.
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture2> const& source,
        std::shared_ptr<gte::Texture2> const& stateTm1,
        std::shared_ptr<gte::Texture2> const& stateT);

private:
    int mNumXGroups, mNumYGroups;
    std::shared_ptr<gte::ComputeShader> mComputeUpdateState;
    std::shared_ptr<gte::SamplerState> mAdvectionSampler;
    std::shared_ptr<gte::Texture2> mUpdateState;

    static std::string const msHLSLUpdateStateString;
};

}
