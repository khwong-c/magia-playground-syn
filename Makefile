all:
	cd function/magia2sv && ./update_magia.sh
	cd function/yosys2digital && npm run build
	cd function/yosys2svg && npm run build
	cd www/src/examples && python compile_index.py
	cd www/ && yarn run build
deploy:
	pulumi up -y
