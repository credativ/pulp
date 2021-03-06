# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
 config.vm.box = "https://download.gluster.org/pub/gluster/purpleidea/vagrant/fedora-21/fedora-21.box"
 # By default, Vagrant wants to mount the code in /vagrant with NFSv3, which will fail. Let's
 # explicitly mount the code using NFSv4.
 config.vm.synced_folder ".", "/vagrant", type: "nfs", nfs_version: 4, nfs_udp: false

 config.vm.provision "ansible" do |ansible|
     ansible.playbook = "playpen/ansible/playbook.yml"
 end

 if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
    config.cache.synced_folder_opts = {
        type: :nfs,
        mount_options: ['rw', 'vers=4', 'tcp']
    }
 end

 # Create the "dev" box
 config.vm.define "dev" do |dev|
    dev.vm.host_name = "pulp-devel"
    dev.vm.synced_folder "..", "/home/vagrant/devel", type: "nfs", nfs_version: 4, nfs_udp: false

    dev.vm.provider :libvirt do |domain|
        domain.memory = 2048
        domain.cpus   = 4
    end

    dev.vm.provision "shell", inline: "sudo -u vagrant bash -e /home/vagrant/devel/pulp/playpen/vagrant-setup.sh"
 end
end
