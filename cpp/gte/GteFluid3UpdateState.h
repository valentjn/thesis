// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteComputeShader.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteFluid3Parameters.h>
#include <gte/GteTexture3.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Fluid3UpdateState
{
public:
    // Construction and destruction.
    ~Fluid3UpdateState();
    Fluid3UpdateState(int xSize, int ySize, int zSize, int numXThreads,
        int numYThreads, int numZThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Member access.  The texels are (velocity.xyz, density).
    std::shared_ptr<gte::Texture3> const& GetUpdateState() const;

    // Update the state for the fluid simulation.
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture3> const& source,
        std::shared_ptr<gte::Texture3> const& stateTm1,
        std::shared_ptr<gte::Texture3> const& stateT);

private:
    int mNumXGroups, mNumYGroups, mNumZGroups;
    std::shared_ptr<gte::ComputeShader> mComputeUpdateState;
    std::shared_ptr<gte::SamplerState> mAdvectionSampler;
    std::shared_ptr<gte::Texture3> mUpdateState;

    static std::string const msHLSLUpdateStateString;
};

}
