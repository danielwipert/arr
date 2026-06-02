A new compression technique for large language models picks which parts to replace one submodule at a time, not layer by layer, and keeps more of the model's original capability.

The method, called SUBFIT, was developed by researchers at the University of Trento. It removes individual attention and feed-forward submodules from a pretrained model and fits a lightweight, custom bypass for each one, using only calibration data. At 25% sparsity, the method retains 84.6% of the dense model's downstream accuracy, against 81.6% for the strongest baseline.

The result is narrower than it sounds. The technique adds explicit compensation parameters for each removed submodule, which increases the deployed model's size by roughly 10% of the removed parameters. This overhead is the price paid for the improved accuracy retention.

For teams deploying models under tight constraints, the finding suggests a trade-off: you can recover more performance if you're willing to store a small, fitted bypass for each removed component, rather than deleting them outright or using a single, folded transformation. It's a question of whether your bottleneck is pure parameter count or a more nuanced balance of memory and accuracy.

Worth reading if you are evaluating structured compression for production. Worth ignoring if your deployment is strictly parameter-bound.

Paper: From Layers to Submodules: Rethinking Granularity in Replacement-Based LLM Compression, Cunegatti et al.
https://arxiv.org/abs/2606.02559

#LLMs #ModelCompression #Inference #Deployment #SUBFIT