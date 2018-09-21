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

class GTE_IMPEXP Fluid3ComputeDivergence
{
public:
    // Construction and destruction.  Compute the divergence of the velocity
    // vector field:  Divergence(V(x,y,z)) = dV/dx + dV/dy + dV/dz.  The
    // derivatives are estimated using centered finite differences,
    //   dV/dx = (V(x+dx,y,z) - V(x-dx,y,z))/(2*dx)
    //   dV/dy = (V(x,y+dy,z) - V(x,y-dy,z))/(2*dy)
    //   dV/dz = (V(x,y,z+dz) - V(x,y,z-dz))/(2*dz)
    ~Fluid3ComputeDivergence();
    Fluid3ComputeDivergence(int xSize, int ySize, int zSize, int numXThreads,
        int numYThreads, int numZThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters);

    // Member access.
    std::shared_ptr<gte::Texture3> const& GetDivergence() const;

    // Compute the divergence of the velocity vector field for the input
    // state.
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture3> const& state);

private:
    int mNumXGroups, mNumYGroups, mNumZGroups;
    std::shared_ptr<gte::ComputeShader> mComputeDivergence;
    std::shared_ptr<gte::Texture3> mDivergence;

    static std::string const msHLSLComputeDivergenceString;
};

}
