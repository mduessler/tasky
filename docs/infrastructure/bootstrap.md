# Bootstrap Documentation

This document gives and overview, usage, and an explanation about design choices
done in the backend of this project. The backend has to be initialized only once.
A backend was implemented, to store the *Terraform state (TFstate)* of the
infrastructure remote. Like this all developers can use the same *TFstate*. The
backend also stored its own *TFstate* remote.
