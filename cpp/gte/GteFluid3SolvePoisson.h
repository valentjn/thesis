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

class GTE_IMPEXP Fluid3SolvePoisson
{
public:
    // Construction and destruction.  Solve the Poisson equation.
    // numIterations: number of Gauss-Seidel steps to use in Execute
    ~Fluid3SolvePoisson();
    Fluid3SolvePoisson(int xSize, int ySize, int zSize, int numXThreads,
        int numYThreads, int numZThreads,
        std::shared_ptr<gte::ConstantBuffer> const& parameters,
        int numIterations);

    // Member access.  The texels are (velocity.xyz, density).
    std::shared_ptr<gte::Texture3> const& GetPoisson() const;

    // Update the state for the fluid simulation.
    void Execute(gte::DX11Engine* engine,
        std::shared_ptr<gte::Texture3> const& divergence);

private:
    int mNumXGroups, mNumYGroups, mNumZGroups;
    std::shared_ptr<gte::ComputeShader> mZeroPoisson;
    std::shared_ptr<gte::ComputeShader> mSolvePoisson;
    std::shared_ptr<gte::ComputeShader> mWriteXFace;
    std::shared_ptr<gte::ComputeShader> mWriteYFace;
    std::shared_ptr<gte::ComputeShader> mWriteZFace;
    std::shared_ptr<gte::Texture3> mPoisson0;
    std::shared_ptr<gte::Texture3> mPoisson1;
    int mNumIterations;

    static std::string const msHLSLZeroPoissonString;
    static std::string const msHLSLSolvePoissonString;
    static std::string const msHLSLEnforcePoissonBoundaryString;
};

}
