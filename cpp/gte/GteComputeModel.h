// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.4.0 (2014/09/25)

#pragma once

#include <gte/GTEngineDEF.h>

// The ComputeModel class allows you to select the type of hardware to use
// in your computational algorithms.
//
// If your computational algorithm requires the GPU, set 'inEngine' to the
// object that will execute the compute shaders.  If your algorithm
// requires CPU multithreading, set the 'inNumThreads' to the desired
// number of threads, presumably 2 or larger.  You can query for the number
// of concurrent hardware threads using std::thread::hardware_concurrency().
// If you want single-threaded computations (on the main thread), set
// inNumThreads to 1.  An example of using this class is
//
//  ComputeModel cmodel(...);
//  if (cmodel.engine)
//  {
//      ComputeUsingGPU(...);
//  }
//  else if (cmodel.numThreads > 1)
//  {
//      ComputeUsingCPUMultipleThreads();
//  }
//  else
//  {
//      ComputeUsingCPUSingleThread();
//  }
// See GenerateMeshUV<Real>::SolveSystem(...) for a concrete example.
//
// Of course, your algorithm can interpret cmodel anyway it likes.  For
// example, you might ignore cmodel.engine if all you care about is
// multithreading on the CPU.


#if defined(WIN32)
#include <GteDX11Engine.h>
#endif

namespace gte
{

class GTE_IMPEXP ComputeModel
{
public:
    // Construction and destruction.  You may derive from this class to make
    // additional behavior available to your algorithms.  For example, you
    // might add a callback function to report progress of the algorithm.
    virtual ~ComputeModel();
    ComputeModel();
    ComputeModel(unsigned int inNumThreads);
    unsigned int numThreads;

#if defined(WIN32)
    ComputeModel(DX11Engine* inEngine, unsigned int inNumThreads);
    DX11Engine* engine;
#endif
};

}
