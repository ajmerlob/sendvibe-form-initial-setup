rm lambda-form-setup.zip
cd env/lib/python2.7/site-packages/
zip -r9 ../../../../lambda-form-setup.zip *
cd ../../../../
zip -g lambda-form-setup.zip form-setup.py
zip -g lambda-form-setup.zip typeform.py
