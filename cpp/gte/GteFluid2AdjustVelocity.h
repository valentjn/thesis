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

class GTE_IMPEXP Fluid2AdjustVelocity
{
public:
    // Construction and destruction.  Adjust the velocities using the
    // solution to the Poisson equation.
    ~Fluid2AdjustVelocity();
    Fluid2AdjustVelocity(int xSize, int ySize, int numXThreads,
        int numYThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Update the state for the fluid simulation.
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture2> const& inState,
        std::shared_ptr<gte::Texture2> const& poisson,
        std::shared_ptr<gte::Texture2> const& outState);

private:
    int mNumXGroups, mNumYGroups;
    std::shared_ptr<gte::ComputeShader> mAdjustVelocity;

    static std::string const msHLSLAdjustVelocityString;
};

}
