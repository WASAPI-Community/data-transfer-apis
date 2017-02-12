# LOCKSS WASAPI implementation

Code related to the LOCKSS implementation of the WASAPI general specification.

* The default_controller.py generated from the WASAPI API spec by FLASK as modified to interface to the LOCKSS daemon's SOAP-y export API.
* A minimal WASAPI client just sufficient to test the server.

Note that the server has XXX comments mostly about mismatches between the LOCKSS SOAP-y API and WASAPI.

This works, in that a LOCKSS daemon in our test framework can be run, create an AU full of synthetic content, export it via WASAPI and HTTP, and verify the SHA1 of the result. Not tested at scale yet. Will need fixing when some suggested changes are made to the LOCKSS daemon.
