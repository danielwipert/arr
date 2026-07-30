A new pair of open retrieval models shows that the choice between dense and late-interaction architectures matters most when searching across languages you haven't trained on.

Researchers at LightOn rebuilt a frontier retrieval training recipe entirely from public data, releasing DENSEON and LATEON, two 149M-parameter models that achieve 56.20 and 57.22 average nDCG@10 on BEIR respectively. They then scaled this approach to multilingual retrieval by translating their English training corpus into eight languages, creating MDENSEON and MLATEON.

The key finding emerged when testing on languages outside the training set. On the full MIRACL benchmark covering 18 languages, MDENSEON scored 58.02 while MLATEON reached 67.04. This nine-point gap demonstrates that late-interaction models transfer more effectively to unseen languages and scripts than their dense counterparts.

For teams building multilingual search systems, this suggests late-interaction architectures may offer better coverage for languages where training data is scarce. The open release of models, data, and code provides a reproducible baseline for evaluating retrieval systems beyond English.

Worth considering when choosing retrieval architectures for global applications.

Paper: DenseOn with the LateOn: Fully Open Dense and Late-Interaction Models for Multilingual, Long-Context, and Code Search, Sourty et al.
https://arxiv.org/abs/2607.27178

#Retrieval #Multilingual #OpenSource #ModelArchitecture #TranslateTrain