require_relative 'boot'

require 'rails/all'

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module RailsOnEcs
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 5.2

    config.log_levels   = :debug
    config.log_tags     = [:subdomain, :uuid]
    config.logger       = ActiveSupport::TaggedLogging.new(Logger.new(STDOUT))

    config.cache_store  = :redis_store, ENV['CACHE_URL'],
                          { namespace: 'rails::cache' }
  end
end
