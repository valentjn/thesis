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

class GTE_IMPEXP Fluid2ComputeDivergence
{
public:
    // Construction and destruction.  Compute the divergence of the velocity
    // vector field:  Divergence(V(x,y)) = dV/dx + dV/dy.  The derivatives are
    // estimated using centered finite differences,
    //   dV/dx = (V(x+dx,y) - V(x-dx,y))/(2*dx)
    //   dV/dy = (V(x,y+dy) - V(x,y-dy))/(2*dy)
    ~Fluid2ComputeDivergence();
    Fluid2ComputeDivergence(int xSize, int ySize, int numXThreads,
        int numYThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Member access.
    std::shared_ptr<gte::Texture2> const& GetDivergence() const;

    // Compute the divergence of the velocity vector field for the input
    // state.
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture2> const& state);

private:
    int mNumXGroups, mNumYGroups;
    std::shared_ptr<gte::ComputeShader> mComputeDivergence;
    std::shared_ptr<gte::Texture2> mDivergence;

    static std::string const msHLSLComputeDivergenceString;
};

}
