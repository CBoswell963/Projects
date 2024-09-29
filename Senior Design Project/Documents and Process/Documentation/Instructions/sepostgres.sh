function prompt {
  echo "Press enter to continue"
  read line
  echo
}

echo "Installing dependencies..."
prompt
sudo yum install readline-devel
sudo yum install zlib-devel
sudo yum install libselinux-devel
sudo yum install bison
sudo yum install gcc
sudo yum install flex

echo "Cloning postgres repo..."
prompt
git clone https://github.com/postgres/postgres.git

echo "Configuring..."
prompt
cd postgres
./configure --enable-debug --enable-cassert --with-selinux

echo "Installing from repo..."
prompt
sudo make
sudo make install

echo "Installing from sepgsql..."
prompt
cd /home/maintuser/postgres/contrib/sepgsql/
sudo make
sudo make install

echo "Initializing postgres..."
prompt
sudo adduser postgres

echo "You are about to edit the sudo file"
echo "Scroll down to the line containing:"
echo "    root    ALL=(ALL)       ALL"
echo "Underneath that line, add:"
echo "    postgres ALL=(ALL)      NOPASSWD:ALL"
echo "Also, comment out the line containing:"
echo "    %wheel        ALL=(ALL)       ALL"
echo "Uncomment the line containing:"
echo "    # %wheel  ALL=(ALL)       NOPASSWD: ALL"
prompt
sudo visudo

sudo mv postgres.service /usr/lib/systemd/system/
sudo chown postgres /usr/local/pgsql/
sudo -i -u postgres /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data --no-locale

echo "You are about to edit postgresql.conf"
echo "Scroll down near the bottom to the line containing:"
echo "    #shared_preload_libraries = ''"
echo "Change it to:"
echo "    shared_preload_libraries = 'sepgsql'"
prompt
sudo -i -u postgres nano /usr/local/pgsql/data/postgresql.conf

sudo systemctl daemon-reload
sudo systemctl enable postgres
sudo -i -u postgres /usr/local/pgsql/bin/postgres --single -F -O -c exit_on_error=true -D /usr/local/pgsql/data postgres < /usr/local/pgsql/share/contrib/sepgsql.sql > /dev/null
sudo -i -u postgres /usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data/ start


echo "About to start postgres..."
prompt
sudo -i -u postgres /usr/local/pgsql/bin/psql
