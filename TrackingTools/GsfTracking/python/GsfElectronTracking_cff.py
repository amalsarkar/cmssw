import FWCore.ParameterSet.Config as cms

from RecoParticleFlow.PFTracking.trackerDrivenElectronSeeds_cff import *
from RecoEgamma.EgammaElectronProducers.ecalDrivenElectronSeeds_cfi import *
from RecoParticleFlow.PFTracking.mergedElectronSeeds_cfi import *

electronSeedsTask = cms.Task(trackerDrivenElectronSeeds,ecalDrivenElectronSeeds,electronMergedSeeds) 
electronSeeds = cms.Sequence(electronSeedsTask)
_electronSeedsTaskFromMultiCl = electronSeedsTask.copy()
_electronSeedsTaskFromMultiCl.add(ecalDrivenElectronSeedsFromMultiCl,electronMergedSeedsFromMultiCl)
_electronSeedsFromMultiCl = cms.Sequence(_electronSeedsTaskFromMultiCl)

from Configuration.Eras.Modifier_phase2_hgcal_cff import phase2_hgcal
phase2_hgcal.toReplaceWith(
  electronSeeds, _electronSeedsFromMultiCl )

from Configuration.Eras.Modifier_fastSim_cff import fastSim
_fastSim_electronSeedsTask = electronSeedsTask.copy()
_fastSim_electronSeedsTask.replace(trackerDrivenElectronSeeds, cms.Task(trackerDrivenElectronSeedsTmp,trackerDrivenElectronSeeds))
fastSim.toReplaceWith(electronSeedsTask, _fastSim_electronSeedsTask)
# replace the ECAL driven electron track candidates with the FastSim emulated ones
import FastSimulation.Tracking.electronCkfTrackCandidates_cff
fastElectronCkfTrackCandidates = FastSimulation.Tracking.electronCkfTrackCandidates_cff.electronCkfTrackCandidates.clone()


from TrackingTools.GsfTracking.CkfElectronCandidateMaker_cff import *
from TrackingTools.GsfTracking.GsfElectronGsfFit_cff import *
electronGsfTracking = cms.Sequence(electronSeeds*electronCkfTrackCandidates*electronGsfTracks)
_electronGsfTracking = electronGsfTracking.copy()
_electronGsfTracking += cms.Sequence(electronCkfTrackCandidatesFromMultiCl*electronGsfTracksFromMultiCl)
_fastSim_electronGsfTracking = electronGsfTracking.copy()
_fastSim_electronGsfTracking.replace(electronCkfTrackCandidates,fastElectronCkfTrackCandidates)
fastSim.toReplaceWith(electronGsfTracking,_fastSim_electronGsfTracking)

from Configuration.Eras.Modifier_phase2_hgcal_cff import phase2_hgcal
phase2_hgcal.toReplaceWith(
  electronGsfTracking, _electronGsfTracking
)

from SimTracker.TrackAssociation.trackTimeValueMapProducer_cfi import trackTimeValueMapProducer
gsfTrackTimeValueMapProducer = trackTimeValueMapProducer.clone(trackSrc = cms.InputTag('electronGsfTracks'))

electronGsfTrackingWithTiming = cms.Sequence(electronGsfTracking.copy()*gsfTrackTimeValueMapProducer)

from Configuration.Eras.Modifier_phase2_timing_cff import phase2_timing
phase2_timing.toReplaceWith(electronGsfTracking, electronGsfTrackingWithTiming)
